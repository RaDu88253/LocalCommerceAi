import os
import json
from tavily import TavilyClient

import googlemaps
import requests
from pytrends.request import TrendReq
from datetime import datetime

from typing import List

class ShoppingTool:
    """A tool with methods for finding stores and products."""
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        self.gmaps_client = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])

    def find_local_stores_tavily(self, query: str, location: str) -> str:
        """
        Finds local small businesses based on a query and location.
        Favors small, local boutiques and clothing stores.
        """
        search_query = f"small local {query} within 5 miles of {location}"
        print(f"---🔍 Searching for businesses with query: '{search_query}'---")
        try:
            results = self.tavily_client.search(
                query=search_query,
                search_depth="advanced",
                max_results=3, # Limit to top 3 stores to keep it focused
                include_domains=["yelp.com", "google.com/maps"] # Focus on directories
            )
            return json.dumps(results.get('results', []), indent=2)
        except Exception as e:
            return f"Error searching for businesses: {e}"

    def find_local_stores_gmaps(self, query: str, location_coords: dict) -> list:
        """
        Finds local stores using Google Maps API based on lat/lng coordinates.
        """
        try:
            print(f"---🔍 Searching Google Maps for '{query}' near {location_coords}---")
            # Step 1: Find nearby places to get their place_id
            places_result = self.gmaps_client.places_nearby(
                location=location_coords,
                keyword=query,
                radius=5000,
                type='clothing_store',
            )

            detailed_results = []
            # Step 2: For each place, make a "Place Details" request to get the website
            for place in places_result.get('results', []):
                place_id = place.get('place_id')
                if not place_id:
                    continue
                
                try:
                    print(f"      -> Fetching details for place_id: {place_id}")
                    # Corrected: 'types' is not a valid field for a Place Details request.
                    # We will get it from the initial search result.
                    fields_to_request = ['name', 'website', 'user_ratings_total', 'business_status', 'place_id', 'rating', 'vicinity']
                    details = self.gmaps_client.place(place_id=place_id, fields=fields_to_request, language='en')
                    if details.get('result'):
                        # Manually add the 'types' from the original search result.
                        details['result']['types'] = place.get('types', [])
                        detailed_results.append(details['result'])
                except Exception as e:
                    print(f"      -> ❌ FAILED to get details for place_id {place_id}. Error: {e}")
                    # Continue to the next place instead of failing the whole search
                    continue

            return detailed_results

        except Exception as e:
            print(f"Error during Google Maps search: {e}")
            return []

    def check_business_scale(self, store_name: str) -> str:
        """
        Performs a web search to find signals of a business being a large chain or corporation.
        """
        # Queries designed to find multiple locations or corporate structure, now in Romanian
        search_query = f'"{store_name}" locații magazine OR "despre noi" OR "relații cu investitorii"'
        print(f"---🕵️  Cross-checking business scale for: '{store_name}'---")
        try:
            results = self.tavily_client.search(query=search_query, max_results=3)
            return json.dumps(results.get('results', []), indent=2)
        except Exception as e:
            return f"Error checking business scale: {e}"

    def get_business_cui(self, store_name: str) -> str | None:
        """
        Searches the web for the CUI (Cod Unic de Înregistrare) of a Romanian business.
        """
        search_query = f'CUI firma "{store_name}"'
        print(f"---🆔 Searching for CUI for: '{store_name}'---")
        try:
            # Use a simple search, as we just need to extract a number
            results = self.tavily_client.search(query=search_query, max_results=1, search_depth="basic")
            if results and results.get('results') and results['results'][0].get('content'):
                # This regex looks for an optional "RO" prefix followed by 2 to 10 digits.
                # This is a much more specific pattern for a CUI/VAT code.
                import re
                match = re.search(r'(?:RO)?(\d{2,10})', results['results'][0]['content'])
                if match:
                    # The actual CUI is the numeric part.
                    cui = match.group(1)
                    print(f"      -> Found potential CUI: {cui}")
                    return cui
            return None
        except Exception as e:
            return f"Error searching for CUI: {e}"

    def verify_anaf_status(self, cui: str) -> bool:
        """
        Verifies if a CUI corresponds to an active taxpayer using the ANAF API.
        """
        print(f"---💼 Verifying ANAF status for CUI: {cui}---")
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            payload = [{"cui": cui, "data": today}]
            response = requests.post("https://webservicesp.anaf.ro/PlatitorTvaRest/api/v8/ws/tva", json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get('found') and data['found'][0]['scpTVA']:
                print("      -> Status: Active VAT Payer.")
                return True
            return False
        except Exception as e:
            print(f"      -> ANAF verification failed: {e}")
            return False

    def get_google_trends(self, store_name: str) -> dict:
        """
        Gets Google Trends data for a specific store name in Romania.
        """
        print(f"---📈 Getting Google Trends for: '{store_name}'---")
        self.pytrends.build_payload(kw_list=[store_name], geo='RO', timeframe='today 1-m')
        return self.pytrends.interest_over_time()

    def get_pytrends(self):
        if not hasattr(self, '_pytrends'):
            self._pytrends = TrendReq(hl='ro-RO', tz=360)
        return self._pytrends

    def search_product_at_store(self, store_website: str, product_query: str) -> str:
        """Searches a specific store's online presence for a product."""
        search_query = f"'{product_query}' site:{store_website}"
        print(f"---👕 Searching for product with query: '{search_query}'---")
        try:
            results = self.tavily_client.search(
                query=search_query,
                max_results=2
            )
            return json.dumps(results.get('results', []), indent=2)
        except Exception as e:
            return f"Error searching for product: {e}"

    def scrape_website_content(self, url: str) -> str:
        """
        Scrapes the text content from a given URL.
        """
        print(f"---🕸️ Scraping content from: {url} ---")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Use .get_text() to more reliably extract only the visible,
            # human-readable text from the page, ignoring scripts and styles.
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"      -> ❌ FAILED to scrape website. Error: {e}")
            return ""

    def translate_terms(self, terms: List[str], target_language: str = "ro") -> List[str]:
        """
        Translates a list of terms to the target language using Google Translate API.
        """
        if not terms:
            return []

        print(f"---🌐 Translating terms to '{target_language}': {terms} ---")
        try:
            api_key = os.environ["GOOGLE_TRANSLATE_API_KEY"]
            url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
            
            payload = {
                'q': terms,
                'target': target_language
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return [item['translatedText'] for item in data['data']['translations']]
        except Exception as e:
            print(f"      -> ❌ FAILED to translate terms. Error: {e}")
            return terms # Fallback to original terms on error
