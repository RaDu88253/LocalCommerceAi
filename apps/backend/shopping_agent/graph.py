import os
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END

from .tools import find_local_businesses, search_product_at_store, Business
from langchain_openai import ChatOpenAI

# --- Agent State ---
class ShoppingAgentState(TypedDict):
    user_query: str
    user_location: dict
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    search_keywords: str  # Keywords extracted for searching
    main_product: str # The main product category, e.g., "jacket"
    businesses: List[Business]
    is_clothing_query: bool # To store the classification result
    

# --- LLM Configuration ---
# Ensure you have OPENAI_API_KEY set in your .env file
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Agent Nodes ---
def query_classifier_node(state: ShoppingAgentState):
    """
    Classifies if the user query is about buying clothing.
    """
    user_query = state["user_query"]
    
    classification_prompt = f"""
    Does the following user query explicitly state an intention to search for or buy a clothing item?
    Answer with only "yes" or "no".

    User query: "{user_query}"
    """
    
    response = llm.invoke([SystemMessage(content=classification_prompt)])
    answer = response.content.strip().lower()
    
    return {"is_clothing_query": "yes" in answer}

def query_extractor_node(state: ShoppingAgentState):
    """
    Extracts relevant search keywords from the user's query using an LLM.
    """
    user_query = state["user_query"]
    
    extraction_prompt = f"""
    From the following user query, extract the specific product with its attributes, and also the main product category.
    Return a JSON object with two keys: "search_keywords" and "main_product".

    Example:
    User query: "Vreau să cumpăr o jachetă neagră de piele."
    Output: {{"search_keywords": "jachetă neagră de piele", "main_product": "jachetă"}}
    
    User query: "{user_query}"
    """
    
    response = llm.invoke([SystemMessage(content=extraction_prompt)])
    import json
    # The LLM should return a JSON string, so we parse it.
    extracted_data = json.loads(response.content)
    
    return {"search_keywords": extracted_data.get("search_keywords"), "main_product": extracted_data.get("main_product")}

def business_finder_node(state: ShoppingAgentState):
    """This node runs the tool to find businesses."""
    # Use the original user_query for finding general store types
    tool_output = find_local_businesses(state) 
    return {"businesses": tool_output.get("businesses", [])}

def product_search_node(state: ShoppingAgentState):
    """This node searches for the product on each business's website."""
    # Use the extracted keywords for a precise product search
    search_keywords = state["search_keywords"]
    main_product = state["main_product"]
    businesses = state["businesses"]
    
    for business in businesses:
        if business.get("website"):
            business["product_found"] = False
            business["product_url"] = None

            search_response = search_product_at_store(business["website"], search_keywords)
            search_results = search_response.get("results", [])

            # Iterăm prin rezultatele căutării pentru o verificare inteligentă
            for result in search_results:
                page_content = result.get("content", "")
                page_url = result.get("url")

                verification_prompt = f"""
                Analyze the following text from a webpage.
                First, does it confirm that the specific product "{search_keywords}" is available for sale?
                If not, does it at least strongly suggest that the general product category "{main_product}" is sold on this page (e.g., it's a category page)?
                
                Answer with "yes" for the specific product, "category" for the general product, or "no" if neither is likely.

                Text: "{page_content}"
                """
                response = llm.invoke([SystemMessage(content=verification_prompt)])
                answer = response.content.strip().lower()

                if "yes" in answer or "category" in answer:
                    # Am găsit o potrivire confirmată de LLM
                    business["product_found"] = True
                    business["product_url"] = page_url
                    break # Oprim căutarea la primul rezultat confirmat

    return {"businesses": businesses}

def response_synthesizer_node(state: ShoppingAgentState):
    """
    This node synthesizes the final, user-facing response based on
    the businesses found and product search results.
    """
    system_prompt = """You are a helpful local shopping assistant.
Your goal is to help users find products from local businesses.
Based on the list of businesses provided, generate a friendly, helpful, and concise response in Romanian. Do not add any descriptions.

For each business, include its name and address.
If the product was found on their website, you MUST provide the direct link to the product page. If not, or if they don't have a website, say that the availability should be checked directly at their physical location. Do not include Google Maps links.
If no businesses were found, apologize and say you couldn't find any matching local stores.

Here is the list of businesses and their details:
{businesses}
"""
    
    # Sort businesses by score in ascending order to show smaller ones first.
    sorted_businesses = sorted(state["businesses"], key=lambda b: b.get("score", float('inf')))

    business_strings = []
    for b in sorted_businesses:
        link_info = f"Link produs: {b['product_url']}" if b.get("product_found") and b.get("product_url") else "Verifică disponibilitatea în magazin."
        business_strings.append(f"- Nume: {b['name']}, Adresă: {b['address']}. {link_info}")
    
    business_list_str = "\n".join(business_strings)
    
    if not state["businesses"]:
        business_list_str = "No businesses found."

    final_prompt = system_prompt.format(businesses=business_list_str)
    
    response = llm.invoke([SystemMessage(content=final_prompt)] + state["messages"])
    return {"messages": [response]}

def predefined_response_node(state: ShoppingAgentState):
    """
    Generates a predefined response for queries not related to clothing.
    """
    predefined_message = "Îmi pare rău, sunt un asistent specializat și pot oferi ajutor doar pentru căutarea de articole de îmbrăcăminte."
    return {"messages": [SystemMessage(content=predefined_message)]}

# --- Conditional Edge Logic ---
def should_continue(state: ShoppingAgentState) -> str:
    """Determines which path to take based on query classification."""
    if state.get("is_clothing_query"):
        return "continue_to_extraction"
    else:
        return "end_with_predefined_response"

# --- Graph Definition ---
builder = StateGraph(ShoppingAgentState)

# Define the nodes
builder.add_node("classify_query", query_classifier_node)
builder.add_node("extract_keywords", query_extractor_node)
builder.add_node("find_businesses", business_finder_node)
builder.add_node("search_for_product", product_search_node)
builder.add_node("synthesize_response", response_synthesizer_node)
builder.add_node("predefined_response", predefined_response_node)

# Define the edges
builder.set_entry_point("classify_query")
builder.add_conditional_edges(
    "classify_query",
    should_continue,
    {
        "continue_to_extraction": "extract_keywords",
        "end_with_predefined_response": "predefined_response",
    },
)
builder.add_edge("extract_keywords", "find_businesses")
builder.add_edge("find_businesses", "search_for_product")
builder.add_edge("search_for_product", "synthesize_response")
builder.add_edge("synthesize_response", END)
builder.add_edge("predefined_response", END)

shopping_graph = builder.compile()
