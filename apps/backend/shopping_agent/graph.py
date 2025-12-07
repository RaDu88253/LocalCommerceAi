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
    main_product: str # The main product category
    attributes: List[str] # The product attributes
    businesses: List[Business]
    is_clothing_query: bool # To store the classification result

# --- LLM Configuration ---
# Ensure you have OPENAI_API_KEY set in your .env file
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Agent Nodes ---
def initialize_state_node(state: ShoppingAgentState):
    """Placeholder for any future initializations."""
    return {}

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
    From the following user query, extract the main product, its attributes, and the full search term.
    Return a JSON object with three keys: "main_product", "attributes" (as a list of strings), and "search_keywords".

    Example:
    User query: "Vreau să cumpăr o jachetă neagră de piele."
    Output: {{"main_product": "jachetă", "attributes": ["neagră", "de piele"], "search_keywords": "jachetă neagră de piele"}}
    
    User query: "{user_query}"
    """
    
    response = llm.invoke([SystemMessage(content=extraction_prompt)])
    import json
    try:
        extracted_data = json.loads(response.content)
    except (json.JSONDecodeError, TypeError):
        # Fallback if JSON parsing fails
        extracted_data = {"search_keywords": user_query, "main_product": user_query.split()[0], "attributes": []}

    return extracted_data

def business_finder_node(state: ShoppingAgentState):
    """This node runs the tool to find businesses."""
    # Force a 5km radius search
    state["search_radius"] = 5000
    tool_output = find_local_businesses(state)
    return {"businesses": tool_output.get("businesses", [])}

def product_search_node(state: ShoppingAgentState):
    """
    Searches for the product on each business's website, validates it,
    and calculates a similarity score.
    """
    search_keywords = state["search_keywords"]
    main_product = state["main_product"]
    attributes = state["attributes"]
    businesses = state["businesses"]
    
    for business in businesses:
        if business.get("website"):
            business["product_found"] = False
            business["product_url"] = None

            # Use the full search keywords for a more specific search on the site.
            tavily_query = f'{search_keywords} site:{business.get("website")}'
            search_response = search_product_at_store(business["website"], tavily_query)
            search_results = search_response.get("results", [])

            for result in search_results:
                page_content = result.get("content", "")
                page_url = result.get("url")

                # Simplified validation: Does the page content match the wanted product?
                verification_prompt = f"""
                Based on the following text from a webpage, does it seem like the product "{search_keywords}" is available for sale?
                Answer with only "yes" or "no".

                Text: "{page_content}"
                """
                response = llm.invoke([SystemMessage(content=verification_prompt)])
                answer = response.content.strip().lower()
                
                if "yes" in answer:
                    # If the LLM confirms the product is on the page, we consider it a valid result.
                    business["product_found"] = True
                    business["product_url"] = page_url
                    # Since we found a valid product, we can stop checking other search results for this business.
                    break

    return {"businesses": businesses}

def response_synthesizer_node(state: ShoppingAgentState):
    """
    This node synthesizes the final, user-facing response based on
    the businesses found and product search results.
    """
    system_prompt = """You are a helpful local shopping assistant.
Your goal is to help users find products from local businesses.
Based on the list of businesses provided, generate a friendly, helpful, and concise response in Romanian with up to 3 recommendations. Do not add any descriptions.

For each business, include its name and address.
You MUST provide the direct link to the product page.
If no businesses were found, apologize and say you couldn't find any matching local stores.

Here are the top businesses found:
{businesses}
"""
    
    # 1. Filter for valid results (must have a product link)
    valid_businesses = [b for b in state.get("businesses", []) if b.get("product_url")]

    # 2. Sort by business score (ascending) to prioritize smaller businesses.
    sorted_businesses = sorted(valid_businesses, key=lambda b: b.get("score", float('inf')))

    # Limit the recommendations to a maximum of 3.
    top_businesses = sorted_businesses[:3]

    business_strings = []
    for b in top_businesses:
        # Now we can be certain that product_url exists.
        link_info = f"Link produs: {b['product_url']}"
        business_strings.append(f"- Nume: {b['name']}, Adresă: {b['address']}. {link_info}")
    
    business_list_str = "\n".join(business_strings)
    
    if not top_businesses:
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
builder.add_node("initialize_state", initialize_state_node)
builder.add_node("classify_query", query_classifier_node)
builder.add_node("extract_keywords", query_extractor_node)
builder.add_node("find_businesses", business_finder_node)
builder.add_node("search_for_product", product_search_node)
builder.add_node("synthesize_response", response_synthesizer_node)
builder.add_node("predefined_response", predefined_response_node)

# Define the edges
builder.set_entry_point("initialize_state")
builder.add_edge("initialize_state", "classify_query")
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
