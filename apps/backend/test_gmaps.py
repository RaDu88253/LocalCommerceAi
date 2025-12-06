import os
import json
from dotenv import load_dotenv
import googlemaps

print("--- Starting Google Maps API Direct Test ---")

# Load environment variables from your .env file
load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    print("❌ ERROR: GOOGLE_MAPS_API_KEY not found in .env file.")
else:
    try:
        print("API Key found. Initializing Google Maps client...")
        gmaps = googlemaps.Client(key=API_KEY)

        # 1. Test Geocoding API
        location_str = "Piața Unirii București"
        print(f"\n--- 🗺️  Testing Geocoding API for: '{location_str}' ---")
        geocode_result = gmaps.geocode(location_str, region='RO')
        print("✅ Geocoding successful. Result:")
        print(json.dumps(geocode_result, indent=2))

        # 2. Test Places API
        location_coords = geocode_result[0]['geometry']['location']
        print(f"\n--- 🔍 Testing Places API near: {location_coords} ---")
        places_result = gmaps.places_nearby(location=location_coords, keyword="magazin de haine", radius=1000)
        print("✅ Places API successful. Found results:")
        print(json.dumps(places_result.get('results', []), indent=2))

    except Exception as e:
        print(f"\n--- ❌ API CALL FAILED ---")
        print("This error is coming directly from the Google Maps library.")
        print("Please check the following:")
        print("  1. Is your API key correct?")
        print("  2. Have you enabled 'Places API' and 'Geocoding API' in your GCP project?")
        print("  3. Is a valid billing account linked to your GCP project?")
        print("\nDetailed Error:")
        print(e)
