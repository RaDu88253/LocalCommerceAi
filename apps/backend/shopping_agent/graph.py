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
    verified_businesses: List[Business] # Accumulator for valid results
    processed_place_ids: set # To avoid re-processing businesses
    search_radius: int # Current search radius
    is_clothing_query: bool # To store the classification result
    
    

# --- LLM Configuration ---
# Ensure you have OPENAI_API_KEY set in your .env file
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Agent Nodes ---
def initialize_state_node(state: ShoppingAgentState):
    """Initializes the state for a new search loop."""
    return {
        "verified_businesses": [],
        "processed_place_ids": set(),
        "search_radius": 5000, # Start with a 5km radius
        "businesses": []
    }

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
    tool_output = find_local_businesses(state)
    
    # Filter out businesses that have already been processed
    all_found = tool_output.get("businesses", [])
    processed_ids = state.get("processed_place_ids", set())
    new_businesses = [b for b in all_found if b.get("place_id") not in processed_ids]
    
    return {"businesses": new_businesses}

def product_search_node(state: ShoppingAgentState):
    """This node searches for the product on each business's website."""
    # Use the extracted keywords for a precise product search
    newly_found_businesses = state["businesses"]
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

    return {"businesses": newly_found_businesses}

def accumulator_and_checker_node(state: ShoppingAgentState):
    """Accumulates verified results and decides if another search loop is needed."""
    newly_processed_businesses = state.get("businesses", [])
    current_verified = state.get("verified_businesses", [])
    
    # Add newly verified businesses to the main list
    for business in newly_processed_businesses:
        if business.get("product_found"):
            current_verified.append(business)
            
    # Update the set of processed place_ids
    processed_ids = state.get("processed_place_ids", set())
    for business in newly_processed_businesses:
        if business.get("place_id"):
            processed_ids.add(business.get("place_id"))
            
    # Increase search radius for the next potential loop
    new_radius = state.get("search_radius", 5000) * 2 # Double the radius
    
    return {
        "verified_businesses": current_verified,
        "processed_place_ids": processed_ids,
        "search_radius": new_radius
    }

def loop_condition_node(state: ShoppingAgentState) -> str:
    """Checks if the loop should continue."""
    verified_count = len(state.get("verified_businesses", []))
    current_radius = state["search_radius"] # Use direct access to get the updated value
    if verified_count >= 3 or current_radius > 20000: # Stop if we have 3 or radius > 20km
        return "end_loop"
    return "continue_loop"

def response_synthesizer_node(state: ShoppingAgentState):
    """
    This node synthesizes the final, user-facing response based on
    the businesses found and product search results.
    """
    system_prompt = """You are a helpful local shopping assistant.
Your goal is to help users find products from local businesses.
Based on the list of businesses provided, generate a friendly, helpful, and concise response in Romanian with a maximum of 3 recommendations. Do not add any descriptions.

For each business, include its name and address.
If the product was found on their website, you MUST provide the direct link to the product page. If not, or if they don't have a website, say that the availability should be checked directly at their physical location. Do not include Google Maps links.
If no businesses were found, apologize and say you couldn't find any matching local stores.

Here are the top businesses found:
{businesses}
"""
    
    # Sort businesses to prioritize those with a found product, then by score.
    # We now only have verified businesses in the list to be shown.
    sorted_businesses = sorted(state["verified_businesses"], key=lambda b: b.get("score", float('inf')))

    # Limit the recommendations to a maximum of 3.
    top_businesses = sorted_businesses[:3]


    business_strings = []
    for b in top_businesses:
        link_info = f"Link produs: {b['product_url']}" if b.get("product_found") and b.get("product_url") else "Verifică disponibilitatea în magazin."
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
builder.add_node("accumulator_and_checker", accumulator_and_checker_node)
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
builder.add_edge("search_for_product", "accumulator_and_checker")
builder.add_conditional_edges(
    "accumulator_and_checker",
    loop_condition_node,
    {
        "continue_loop": "find_businesses", # Loop back to search with a larger radius
        "end_loop": "synthesize_response",
    }
)
builder.add_edge("synthesize_response", END)
builder.add_edge("predefined_response", END)

shopping_graph = builder.compile()
