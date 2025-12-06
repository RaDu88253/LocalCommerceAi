import requests
import json

# The URL of your running FastAPI application
API_URL = "http://127.0.0.1:8000/shopping-assistant"

# The user's shopping query. You can change this to test different products!
user_query = "Vreau să cumpăr o jachetă neagră de piele."

# Example coordinates for Piața Unirii, București
latitude = 44.4268
longitude = 26.1025

# The payload for the POST request
payload = {
    "user_query": user_query,
    "latitude": latitude,
    "longitude": longitude
}

print(f"--- Sending request to: {API_URL} ---")
print(f"--- Query: {user_query} ---\n")

try:
    # Send the POST request with a long timeout, as the agent can take time to think.
    response = requests.post(API_URL, json=payload, timeout=300)

    # Check if the request was successful
    # This will raise an HTTPError if the status code is 4xx or 5xx
    response.raise_for_status()

    print(f"--- ✅ SUCCESS (Status Code: {response.status_code}) ---")
    print("\n--- Agent's Final Response: ---")
    # Try to parse and print the JSON response
    try:
        # Print the 'response' field directly to render newlines correctly
        response_data = response.json()
        print(response_data.get("response", "No 'response' field found in JSON."))
    except json.JSONDecodeError:
        print("--- ⚠️ WARNING: Response was not valid JSON. Displaying raw text: ---")
        print(response.text)

except requests.exceptions.HTTPError as e:
    print(f"\n--- ❌ FAILED with HTTP Error (Status Code: {e.response.status_code}) ---")
    print("The server responded with an error. This is often caused by an issue with an external API key or a bug in the agent's logic.")
    print("\n--- Raw Server Response: ---")
    print(e.response.text)
except requests.exceptions.RequestException as e:
    print(f"\n--- ❌ FAILED to connect to the API: {e} ---")
    print("Please make sure the backend server is running (`uvicorn main:app --reload`).")
