import os
import logging
import re
from typing import List, Dict, Any, TypedDict, Optional

import googlemaps
from tavily import TavilyClient

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Tool State & Configuration ---
class Business(TypedDict):
    """A dictionary representing a verified local business."""
    name: str
    address: str
    rating: float
    maps_url: str
    website: Optional[str]
    product_url: Optional[str]
    score: int

def get_gmaps_client():
    """Initializes and returns a Google Maps client."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set.")
    return googlemaps.Client(key=api_key)

def get_tavily_client():
    """Initializes and returns a Tavily client."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not set.")
    return TavilyClient(api_key=api_key)

def calculate_business_score(business_name: str, total_ratings: int) -> int:
    """
    Calculates a score based on search popularity and number of reviews.
    A lower score indicates a smaller, less-known business.
    """
    logger.info(f"---🕵️  Calculating score for: '{business_name}'---")
    search_popularity_score = 0
    try:
        tavily = get_tavily_client()
        # A general search for the business name. More results imply higher popularity.
        search_query = f'"{business_name}"'
        
        results = tavily.search(
            query=search_query, 
            max_results=5, # Check more results for a better popularity signal
            search_depth="basic"
        )

        if results and results.get('results'):
            search_popularity_score = len(results.get('results')) * 50 # Weight search results

    except Exception as e:
        logger.error(f"      -> Error during score calculation for '{business_name}': {e}")
    
    return total_ratings + search_popularity_score

def find_local_businesses(state: Dict) -> Dict:
    """
    A tool that finds local businesses using Google Maps.
    """
    user_query = state.get("user_query")
    user_location = state.get("user_location")
    logger.info(f"Tool 'find_local_businesses' running for query: '{user_query}'")

    if not user_location:
        return {"businesses": [], "error": "User location is missing."}

    try:
        # Gracefully handle missing API keys instead of crashing the server.
        gmaps = get_gmaps_client()
        get_tavily_client() # We call this just to validate the key is present.
    except ValueError as e:
        logger.error(f"API Key Error: {e}")
        return {"businesses": [], "error": f"A required API key is not configured on the server: {e}"}
    try:
        places_result = gmaps.places_nearby(
            location=user_location,
            keyword=user_query,
            radius=5000,  # Search within a 5km radius
            language="ro",
            type="clothing_store"
        )
        
        verified_businesses: List[Business] = []
        for place in places_result.get("results", []):
            place_name = place.get("name")
            logger.info(f"Found business on map: {place_name}")

            # Obținem detalii suplimentare, inclusiv website-ul
            place_id = place.get('place_id')
            website = None
            total_ratings = place.get('user_ratings_total', 0)

            if place_id:
                try:
                    # Fetch website details in a separate call
                    details = gmaps.place(place_id=place_id, fields=['website'], language='ro')
                    website = details.get('result', {}).get('website')
                except Exception as e:
                    logger.warning(f"Could not fetch details for place_id {place_id}: {e}")

            # Calculăm scorul pe baza popularității în căutări și a numărului de recenzii.
            score = calculate_business_score(place_name, total_ratings)

            verified_businesses.append({
                "name": place_name,
                "address": place.get("vicinity"),
                "rating": place.get("rating", 0),
                "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
                "website": website,
                "score": score,
            })

        return {"businesses": verified_businesses}

    except Exception as e:
        logger.error(f"An error occurred in the business search tool: {e}")
        return {"businesses": [], "error": str(e)}

def search_product_at_store(business_website: str, product_query: str) -> Dict:
    """
    A tool to search a specific store's website for a product using Tavily.
    """
    logger.info(f"---👕 Searching for product '{product_query}' on site: '{business_website}'---")
    if not business_website:
        return {"results": [], "error": "Business website is not available."}
    
    try:
        tavily = get_tavily_client()
        # Use Tavily's site: search operator for a targeted search
        search_query = f"'{product_query}' site:{business_website}"
        results = tavily.search(query=search_query, max_results=3)
        return {"results": results.get('results', [])}
    except Exception as e:
        logger.error(f"An error occurred during product search: {e}")
        return {"results": [], "error": str(e)}
