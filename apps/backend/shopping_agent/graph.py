import json
from typing import List, TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from .tools import ShoppingTool
from urllib.parse import urlparse

# --- State Definition ---

class Product(TypedDict):
    """Represents a product found at a local store."""
    item_name: str
    price: float
    description: str
    store_name: str
    store_address: str
    url: str

class AgentState(TypedDict):
    """Defines the state of our shopping agent graph."""
    user_query: str
    user_location: str
    parsed_query: dict
    local_stores: List[dict]  # Will store {'name': str, 'website': str}
    product_options: List[Product]
    messages: Annotated[list, add_messages]

# --- Agent Nodes ---

# Use a free, local model for query parsing.
llm = ChatOpenAI(model="gpt-4.1-nano")

class ExtractedProductInfo(BaseModel):
    """Represents product info extracted from a webpage."""
    item: str = Field(description="The core clothing item described in the text.")
    color: str = Field(description="The primary color of the clothing item.")

shopping_tool = ShoppingTool()

class ParsedQuery(BaseModel):
    """Structured output for a user's shopping query."""
    item: str = Field(description="The core clothing item the user is looking for.")
    attributes: List[str] = Field(description="A list of descriptive attributes like color, material, style, etc.")

async def query_parser_node(state: AgentState):
    """
    Analizează interogarea utilizatorului într-un format structurat folosind un model lingvistic avansat.
    """
    print("---📝 Analiza interogării utilizatorului cu GPT---")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Ești un expert în analizarea interogărilor de cumpărături. Scopul tău este să extragi obiectul vestimentar de bază (substantivul la singular) și atributele sale descriptive. Nu deduce locația."),
        ("user", "Utilizatorul dorește să cumpere: {query}")
    ])
    
    # Folosește .with_structured_output pentru a obține un JSON curat
    parser_llm = llm.with_structured_output(ParsedQuery)
    chain = prompt | parser_llm
    parsed_output = await chain.ainvoke({"query": state["user_query"]})

    print(f"---✅ Interogare analizată cu succes ---")
    print(f"  - Obiect: {parsed_output.item}")
    print(f"  - Atribute: {parsed_output.attributes}\n")

    return {"parsed_query": parsed_output.dict()}


def score_business(store: dict, business_context: str, anaf_status: bool) -> float:
    """
    Calculates a 'small business' score. A lower score is better.
    Uses multiple data sources for a robust, localized analysis.
    """
    # Normalize the number of ratings. More ratings = higher score (less desirable).
    ratings_count = store.get('user_ratings_total', 0)
    score = min(ratings_count, 500) / 50

    # Check for corporate keywords in the secondary search context
    corporate_keywords = ["locații", "franciză", "investitori", "acțiuni", "carieră", "internațional"]
    context_lower = business_context.lower()
    for keyword in corporate_keywords:
        if keyword in context_lower:
            print(f"      -> Found corporate keyword '{keyword}'. Penalizing score.")
            score += 5 # Apply a heavy penalty

    # Heavily reward businesses that are verified, active taxpayers with ANAF.
    if anaf_status:
        print("      -> ANAF status confirmed. Applying major bonus.")
        score -= 10 # This is a very strong positive signal
    else:
        score += 2 # Unverified businesses are slightly penalized

    # Check business types. 'boutique' is a good sign, 'department_store' is not.
    types = store.get('types', [])
    if 'boutique' in types:
        score -= 2  # Bonus for being a boutique
    if 'department_store' in types:
        score += 5  # Penalty for being a department store

    return score

async def location_finder_node(state: AgentState):
    """Finds local stores using the shopping tool."""
    print("---📍 Finding Local Stores---")
    item = state.get("parsed_query", {}).get("item", "")
    location = state["user_location"]
    
    # Use the new Google Maps tool. Search for both the item and generic terms.
    search_query = f"{item} OR clothing boutique OR magazin de haine"
    store_results = shopping_tool.find_local_stores_gmaps(search_query, location_coords=location)

    # --- Restore printing of all store names ---
    print("\n---🗺️ All Stores Found by Google Maps: ---")
    if not store_results:
        print("  -> No stores found in the area.")
    else:
        # Print the full JSON object for each store for detailed inspection
        print(json.dumps(store_results, indent=2, ensure_ascii=False))
    print("------------------------------------------\n")

    # --- Correctly print all found websites ---
    print("\n---🗺️ All Websites Found by Google Maps: ---")
    all_websites = [store.get("website") for store in store_results if store.get("website")]
    if not all_websites:
        print("  -> No websites were listed in the Google Maps results.")
    for website in all_websites:
        print(f"  - {website}")
    print("------------------------------------------\n")

    # Filter for stores that have a real website, not just a social media page.
    social_media_domains = ["facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com", "tiktok.com"]
    online_stores = []
    invalid_websites = []
    for store in store_results:
        website = store.get("website")
        if not website:
            continue

        # Use urlparse to reliably get the domain name for checking
        domain_name = urlparse(website).netloc.replace("www.", "")
        if domain_name in social_media_domains:
            invalid_websites.append(website)
        else:
            online_stores.append(store)

    print("\n---🗺️  Filtered Google Maps Search Results (with valid websites): ---")
    print(f"(Found {len(store_results)} total, {len(online_stores)} have valid websites)")
    
    # If no valid websites are found, list the invalid ones that were filtered out.
    if not online_stores and invalid_websites:
        print("\n---🚫 Invalid or Social Media Websites Found: ---")
        for website in invalid_websites:
            print(f"  - {website}")

    print("----------------------------------------------------------------\n")
    # Score each business using the enhanced scoring function
    scored_stores = []
    print("---🔢 Calculating Business Scores: ---")
    for store in online_stores:
        store_name = store.get("name")
        if not store_name:
            continue
        # Gather data from all our new tools
        context = shopping_tool.check_business_scale(store_name)
        cui = shopping_tool.get_business_cui(store_name)
        anaf_ok = shopping_tool.verify_anaf_status(cui) if cui else False

        score = score_business(store, context, anaf_ok)
        print(f"  - Store: '{store_name}', Score: {score:.2f}")
        scored_stores.append((store, score))

    sorted_stores = sorted(scored_stores, key=lambda item: item[1])
    print("\n---🏆 Final Sorted Businesses (Top 3): ---")
    for store, score in sorted_stores[:3]:
        print(f"  - Store: '{store['name']}', Final Score: {score:.2f}")
    print("------------------------------------------\n")

    return {"local_stores": sorted_stores}

async def product_searcher_node(state: AgentState):
    """Searches for the product in each identified local store."""
    print("---🛍️ Searching for Products in Stores---")
    # Use the parsed English terms for searching
    parsed_query = state.get("parsed_query", {})
    item = parsed_query.get("item", "")
    attributes = parsed_query.get("attributes", [])
    product_query = f"{item} {' '.join(attributes)}".strip()

    stores = state["local_stores"]
    all_product_options = []

    # --- New Tiered Search Logic ---
    tier1_stores = [s[0] for s in stores[:3]]      # Top 3 small businesses
    tier2_stores = [s[0] for s in stores[3:10]]   # Next 7 medium businesses
    tier3_stores = [s[0] for s in stores[10:]]     # All other large businesses

    search_tiers = [
        ("Nivel 1 (Magazine Mici)", tier1_stores),
        ("Nivel 2 (Magazine Medii)", tier2_stores),
        ("Nivel 3 (Magazine Mari)", tier3_stores)
    ]

    for tier_name, tier_stores in search_tiers:
        if not tier_stores:
            continue

        print(f"\n--- Căutare în {tier_name} ---")
        for store in tier_stores:
            store_name = store.get("name")
            store_website = store.get("website")
            if not store_website:
                continue

            product_results_json = shopping_tool.search_product_at_store(store_website, product_query)
            try:
                product_results = json.loads(product_results_json)
            except json.JSONDecodeError:
                print(f"      -> ⚠️  Could not decode search results for {store_name}. Skipping.")
                continue

            for res in product_results:
                product_url = res.get('url')
                if not product_url:
                    continue

                # --- New: Validate that the product URL belongs to the store's website ---
                store_domain = urlparse(store_website).netloc.replace("www.", "")
                product_domain = urlparse(product_url).netloc.replace("www.", "")
                if store_domain not in product_domain:
                    print(f"      -> ❌ Discarding link to different domain: {product_url}")
                    continue

                # Scrape the actual page content for a much better validation
                page_content = shopping_tool.scrape_website_content(product_url)
                if not page_content:
                    continue
                
                truncated_content = page_content

                # --- New Keyword-Based Validation ---
                page_content_lower = truncated_content.lower()

                # 1. Item must be an exact match (any of its synonyms must be present)
                item_match = item.lower() in page_content_lower
                if not item_match:
                    print(f"      -> ❌ Discarding: Item not found in page content for {product_url}")
                    continue

                all_product_options.append({
                    "store_name": store_name,
                    "item_name": res.get("title"),
                    "url": res.get("url"),
                    "description": res.get("content"),
                    "price": "Price not found",
                })
            
        # După ce a căutat în TOATE magazinele din nivelul curent, verifică dacă a găsit ceva.
        # Dacă da, se oprește și returnează rezultatele, fără a mai trece la nivelurile următoare.
        if all_product_options:
            print(f"\n--- ✅ Am găsit rezultate în {tier_name}. Se oprește căutarea. ---\n")
            return {"product_options": all_product_options}

    return {"product_options": all_product_options}

async def results_synthesizer_node(state: AgentState):
    """Synthesizes the final response to the user."""
    print("---✨ Synthesizing Final Response---")
    if not state["product_options"]:
        return {"messages": [("assistant", "I'm sorry, I couldn't find any matching items in small local stores near you. You could try broadening your search!")]}

    # --- New: Bypass the LLM for formatting and construct the response directly ---
    intro = "I found a few great options for you from local businesses! Here they are:\n\n"
    product_summary = []
    for option in state["product_options"]:
        item_name = option.get('item_name', 'N/A')
        store_name = option.get('store_name', 'N/A')
        url = option.get('url', 'N/A')
        # Ensure store_name is a string, not a dictionary
        if isinstance(store_name, dict):
            store_name = store_name.get('name', 'N/A')
        summary = f"**Item:** {item_name}\n**Store:** {store_name}\n**Link:** {url}\n"
        product_summary.append(summary)
    
    final_response_text = intro + "\n".join(product_summary)
    
    return {"messages": [("assistant", final_response_text)]}

# --- Graph Definition ---

graph_builder = StateGraph(AgentState)

graph_builder.add_node("query_parser", query_parser_node)
graph_builder.add_node("location_finder", location_finder_node)
graph_builder.add_node("product_searcher", product_searcher_node)
graph_builder.add_node("results_synthesizer", results_synthesizer_node)

graph_builder.set_entry_point("query_parser")
graph_builder.add_edge("query_parser", "location_finder")
graph_builder.add_edge("location_finder", "product_searcher")
graph_builder.add_edge("product_searcher", "results_synthesizer")
graph_builder.add_edge("results_synthesizer", END)

shopping_graph = graph_builder.compile()
