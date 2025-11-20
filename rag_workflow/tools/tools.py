from langchain_core.tools import tool 
from langchain_tavily import TavilySearch
import os
import json
import pandas as pd
import PIL.Image
import google.generativeai as genai
from fuzzywuzzy import process
import math
import requests

from dotenv import load_dotenv

load_dotenv()

try:    # try load the csv file of medicine data
    df_medicines = pd.read_csv('medicine_data.csv')
    df_medicines.columns = df_medicines.columns.str.strip()
    # Create lists for fuzzy matching
    MEDICINE_NAMES_LIST = df_medicines['Medicine Name'].dropna().tolist()
    COMPOSITION_LIST = df_medicines['Composition'].dropna().tolist()
    print("INFO: Medicine dataset loaded and prepared for fuzzy matching.")
except FileNotFoundError:
    print("WARNING: 'medicine_data.csv' not found. The database lookup feature will be disabled.")
    df_medicines = None
    MEDICINE_NAMES_LIST = []
    COMPOSITION_LIST = []

# api_key = os.getenv("GOOGLE_API_KEY")
# if not api_key:
#     raise ValueError("GOOGLE_API_KEY not found in .env file.")
# genai.configure(api_key=api_key)


#==========================================================================================


@tool
def calculator(a: float, b: float, operation: str) -> float | str:
    """
    Perform arithmetic operations

    Args: 
        a: float
        b: float
        operation: str (e.g., '+', '-', '*', '/', 'add', 'subtract', 'multiply', 'divide')
    """
    print("Calculator activated")

    # print("a", a)
    # print("b", b)
    # print("operation", operation)
    
    operation = operation.lower()  # normalize input
    
    if operation in ('+', 'add', 'addition'):
        return a + b
    elif operation in ('-', 'sub', 'subtract', 'subtraction'):
        return a - b
    elif operation in ('*', 'mul', 'multiply'):
        return a * b
    elif operation in ('/', 'div', 'divide', 'division'):
        if b == 0:
            return "Error: Division by zero!"
        return a / b
    else:
        return f"Operation '{operation}' not supported."

    

#==================== web search tool ======================================
# to do handle error


tavily_search = TavilySearch(max_results=3)
    

@tool 
def search(query: str) -> str:
    """Takes a query and perform web search"""
    res = tavily_search.invoke(query)

    l = ""
    for i in res['results']:
        l = l + i['content']

    l = l[:500]

    # print("this is l", l)

    return l


# def haversine_distance(lat1, lon1, lat2, lon2):
#     """
#     Calculate the distance between two lat/lon points using Haversine formula.
#     Returns distance in kilometers.
#     """
#     R = 6371  # Earth radius in km

#     d_lat = math.radians(lat2 - lat1)
#     d_lon = math.radians(lon2 - lon1)

#     a = (math.sin(d_lat / 2) ** 2 +
#          math.cos(math.radians(lat1)) *
#          math.cos(math.radians(lat2)) *
#          math.sin(d_lon / 2) ** 2)

#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

#     return R * c


# def find_nearby_hospitals_with_distance(lat, lon, radius=5000):
#     query = f"""
#     [out:json];
#     (
#       node["amenity"="hospital"](around:{radius},{lat},{lon});
#       way["amenity"="hospital"](around:{radius},{lat},{lon});
#       relation["amenity"="hospital"](around:{radius},{lat},{lon});
#     );
#     out center;
#     """

#     url = "https://overpass-api.de/api/interpreter"
#     response = requests.post(url, data={"data": query})
#     data = response.json()

#     hospitals = []

#     for item in data.get("elements", []):
#         name = item.get("tags", {}).get("name", "Unknown Hospital")

#         # Correct lat/lon for nodes, ways, relations
#         if "lat" in item:
#             h_lat = item["lat"]
#             h_lon = item["lon"]
#         else:
#             h_lat = item.get("center", {}).get("lat")
#             h_lon = item.get("center", {}).get("lon")

#         if not h_lat or not h_lon:
#             continue

#         # Calculate distance
#         distance = haversine_distance(lat, lon, h_lat, h_lon)

#         hospitals.append({
#             "name": name,
#             # "latitude": h_lat,
#             # "longitude": h_lon,
#             "distance_km": round(distance, 2)
#         })

#     # Sort by nearest first
#     hospitals.sort(key=lambda x: x["distance_km"])
#     print("this is hos", hospitals)
#     return hospitals

# @tool
# def find_nearby_hospitals(place_name):
#     """use this function to find nearby hospitals."""
#     print("loation", place_name)
#     url = "https://nominatim.openstreetmap.org/search"
#     params = {
#         "q": place_name,
#         "format": "json",
#         "limit": 1
#     }

#     response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
#     data = response.json()

#     if not data:
#         return None
    
#     latitude = float(data[0]["lat"])
#     longitude = float(data[0]["lon"])
#     display_name = data[0]["display_name"]

#     hospitals = find_nearby_hospitals_with_distance(lat=latitude, lon=longitude, radius=5000)
#     print("these are hos", hospitals)
#     return hospitals



# Example: convert location name
# result = geocode_location("NIT Kurukshetra")
# print(result)

# ...existing code...
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two lat/lon points using Haversine formula.
    Returns distance in kilometers.
    """
    # ensure numeric inputs
    # print("lat", lat)
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return float("inf")

    R = 6371  # Earth radius in km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
# ...existing code...

def find_nearby_hospitals_with_distance(lat, long, radius=5000):
    """use this to find nearby hospitals"""
    # print("find nealrnias;fjsif")
    try:
        lat = float(lat)
        long = float(long)
    except (ValueError, TypeError):
        print(f"Invalid coordinates provided: {lat}, {long}")
        return []
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{long});
      way["amenity"="hospital"](around:{radius},{lat},{long});
      relation["amenity"="hospital"](around:{radius},{lat},{long});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={"data": query}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    hospitals = []

    for item in data.get("elements", []):
        name = item.get("tags", {}).get("name", "Unknown Hospital")

        # Prefer node lat/lon, otherwise use center
        if "lat" in item and "lon" in item:
            h_lat = item.get("lat")
            h_lon = item.get("lon")
        else:
            center = item.get("center") or {}
            h_lat = center.get("lat")
            h_lon = center.get("lon")

        # Skip if coordinates missing
        if h_lat is None or h_lon is None:
            continue

        # ensure floats
        try:
            h_lat = float(h_lat)
            h_lon = float(h_lon)
        except (TypeError, ValueError):
            continue

        # Calculate distance
        distance = haversine_distance(lat, long, h_lat, h_lon)

        hospitals.append({
            "name": name,
            "distance_km": round(distance, 2)
        })

    # Sort by nearest first
    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals
# # ...existing code...
@tool
def find_nearby_hospitals(lat: str, long: str):
    """use this function to find nearby hospitals.
    it will receive lat: latitude as string and long: longitude as string"""
    # if preference == 'place_name':
    #     print("nearby tool activatedssssssssssssssss")
    #     url = "https://nominatim.openstreetmap.org/search"
    #     params = {
    #         "q": place_name,
    #         "format": "json",
    #         "limit": 1
    #     }

    #     try:
    #         response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    #         response.raise_for_status()
    #         data = response.json()
    #     except Exception:
    #         return []

    #     if not data:
    #         return []

    #     try:
    #         latitude = float(data[0]["lat"])
    #         longitude = float(data[0]["lon"])
    #     except (KeyError, TypeError, ValueError):
    #         return []

    hospitals = find_nearby_hospitals_with_distance(lat=lat, long=long, radius=5000)
    # print("nearby hos", hospitals)
    return hospitals
# # ...existing code...

# import requests
# from langchain_core.tools import tool

# # Assuming this function exists in your codebase
# # from your_module import find_nearby_hospitals_with_distance

# # @tool
# # def find_nearby_hospitals(lat: str = "", long: str = "", place_name: str = "", preference: str = ""):
# #     """
# #     Use this function to find nearby hospitals.
    
# #     Args:
# #         lat (str): Latitude (required if preference is 'coordinates').
# #         long (str): Longitude (required if preference is 'coordinates').
# #         place_name (str): Name of the city/area (required if preference is 'place_name').
# #         preference (str): The selection logic ('place_name', 'coordinates', 'summary', 'ask_user').
# #     """

# #     print("this is lat", lat)
# #     print("this is long", long)
# #     print("this is place", place_name)
# #     print("this is preference", preference)
# #     # 1. Handle "ask_user" or missing data immediately
# #     if preference == "ask_user":
# #         return "Please provide a specific location name or your GPS coordinates."

# #     target_lat = None
# #     target_lon = None

# #     # 2. Logic Branch A: User provided a Location Name (Highest Priority)
# #     # or 'summary' was chosen but it relies on a place name.
# #     if preference == "place_name":
# #         if not place_name:
# #             return "Error: Preference was set to place_name, but no name was provided."
            
# #         # Geocoding logic (converting name to coordinates)
# #         url = "https://nominatim.openstreetmap.org/search"
# #         params = {
# #             "q": place_name,
# #             "format": "json",
# #             "limit": 1
# #         }

# #         try:
# #             # User-Agent is required by Nominatim Policy
# #             headers = {"User-Agent": "Medical_Assistant_Bot/1.0"} 
# #             response = requests.get(url, params=params, headers=headers, timeout=10)
# #             response.raise_for_status()
# #             data = response.json()
            
# #             if not data:
# #                 return f"Could not find coordinates for the location: {place_name}"
                
# #             target_lat = float(data[0]["lat"])
# #             target_lon = float(data[0]["lon"])
            
# #         except Exception as e:
# #             return f"Error resolving location name: {str(e)}"

# #     # 3. Logic Branch B: User provided Coordinates
# #     # or 'summary' was chosen but it relies on coordinates.
# #     elif preference == "coordinates":
# #         print("this is numming")
# #         try:
# #             target_lat = float(lat)
# #             target_lon = float(long)
# #         except ValueError:
# #             return "Invalid coordinates format provided."
        
# #     print("latlslf", target_lat)
# #     print("latlslf", target_lon)

# #     # 4. Final execution
# #     if target_lat is not None and target_lon is not None:
# #         print("sjflsjf")
# #         # Call your internal calculation function
# #         # Ensure find_nearby_hospitals_with_distance accepts floats or strings as per its definition
# #         print(find_nearby_hospitals_with_distance(lat=target_lat, long=target_lon, radius=5000))
# #         res = find_nearby_hospitals_with_distance(lat=target_lat, long=target_lon, radius=5000)
# #         return res
        
    
# #     return "Unable to determine location for hospital search."


# @tool
# def find_nearby_hospitals(lat: str = "", long: str = "", place_name: str = "", preference: str = ""):
#     """
#     Finds nearby hospitals.
#     Args:
#         lat: Latitude string.
#         long: Longitude string.
#         place_name: City/Area name.
#         preference: 'place_name' or 'coordinates' or 'ask_user'.
#     """
#     print(f"DEBUG: Tool Called. Pref: {preference}, Place: {place_name}, Lat: {lat}, Long: {long}")

#     if preference == "ask_user":
#         return "Please provide a specific location name or allow GPS access."

#     target_lat = None
#     target_lon = None

#     # --- PATH A: Location Name (Prioritized) ---
#     if preference == "place_name":
#         if not place_name:
#             return "Error: logic selected place_name but none provided."
            
#         url = "https://nominatim.openstreetmap.org/search"
#         # OpenStreetMap requires a User-Agent
#         headers = {"User-Agent": "Medical_Assistant_Bot/1.0"} 
        
#         try:
#             resp = requests.get(url, params={"q": place_name, "format": "json", "limit": 1}, headers=headers, timeout=5)
#             resp.raise_for_status()
#             data = resp.json()
            
#             if not data:
#                 return f"Could not find coordinates for '{place_name}'."
                
#             target_lat = float(data[0]["lat"])
#             target_lon = float(data[0]["lon"])
#         except Exception as e:
#             return f"Geocoding error: {e}"

#     # --- PATH B: Coordinates (Fallback) ---
#     elif preference == "coordinates":
#         # Verify we actually have valid numbers, filtering out "None" strings
#         if not lat or not long or lat == "None" or long == "None":
#             return "Error: Coordinate preference selected but invalid coordinates provided."
            
#         try:
#             target_lat = float(lat)
#             target_lon = float(long)
#         except ValueError:
#             return "Invalid coordinate format."

#     # --- FINAL EXECUTION ---
#     if target_lat is not None and target_lon is not None:
#         # Call your existing calculation function
#         res = find_nearby_hospitals_with_distance(lat=target_lat, long=target_lon, radius=5000)
#         return res
    
#     return "Could not determine location."



#================================= medicine label ocr tool ======================================
@tool
def medicine_ocr_tool(image_path: str) -> dict | str:
    """
    The agent must first save any user-uploaded image to a local file path before calling this tool.
    Args:   image_path (str): The local file path to the saved medicine label image.
    """
    print(f"Medicine OCR activated for path: {image_path}")
    image = None
    try:
        
        model = genai.GenerativeModel("gemini-2.5-flash") 
        image = PIL.Image.open(image_path)
        
        # This is the internal prompt for the tool, not the agent prompt
        prompt = """
            Analyze the image of this medicine label. Extract the following information and return it as a clean JSON object.
            Do not include any introductory text or markdown formatting like ```json.
            
            The keys in the JSON should be:
            - "medicine_name"
            - "manufacturer"
            - "active_salts" (as a list of strings)
            - "expiry_date" (in DD-MM-YYYY format if possible, otherwise MM-YYYY)
            
            If a piece of information is not available, set its value to null.
        """
        response = model.generate_content([image, prompt])
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_text)

    except json.JSONDecodeError:
        print("Error: Model returned non-JSON text:", response.text)
        return "Error: Failed to parse model response as JSON."
    except Exception as e:
        print(f"An unexpected error occurred in OCR tool: {e}")
        return f"Error: An internal error occurred during processing: {e}"
    finally:
        if image:
            image.close()


#================================= data related to image tool ======================================
# fuzzy-search
@tool
def medicine_database_lookup_tool(medicine_name: str, active_salts: list) -> dict | str:
    """
    Args:
        medicine_name (str): The name of the medicine (can be null).
        active_salts (list): A list of active salts (can be empty).
    """
    print(f"Medicine DB Fuzzy Lookup for: {medicine_name}, {active_salts}")
    if df_medicines is None or df_medicines.empty:
        return "Error: Medicine database (medicine_data.csv) is not loaded."

    # --- Fuzzy Search by Medicine Name ---
    if medicine_name:
        # Find the best match from the 'Medicine Name' list
        # We set a cutoff score of 85 to avoid bad matches
        match = process.extractOne(medicine_name, MEDICINE_NAMES_LIST, score_cutoff = 85)
         
        if match:
            best_match_name = match[0]
            print(f"Fuzzy match found by name: {medicine_name} -> {best_match_name}")
            # Get the full row from the DataFrame for this match
            name_result = df_medicines[df_medicines['Medicine Name'] == best_match_name]
            if not name_result.empty:
                first_match = name_result.iloc[0]
                return {
                    "uses": first_match.get("Uses"),
                    "side_effects": first_match.get("Side_effects")
                }

    # --- Fallback to Fuzzy Search by Active Salts ---
    if active_salts:
        for salt in active_salts:
            cleaned_salt = salt.split('(')[0].strip()
            if not cleaned_salt:
                continue
                
            # Find the best match from the 'Composition' list
            match = process.extractOne(cleaned_salt, COMPOSITION_LIST, score_cutoff=85)
            
            if match:
                best_match_composition = match[0]
                print(f"Fuzzy match found by salt: {cleaned_salt} -> {best_match_composition}")
                # Get the full row for this composition match
                salt_result = df_medicines[df_medicines['Composition'] == best_match_composition]
                if not salt_result.empty:
                    first_match = salt_result.iloc[0]
                    return {
                        "uses": first_match.get("Uses"),
                        "side_effects": first_match.get("Side_effects")
                    }
                
    return "No information found in the database."
# @tool

# def medicine_database_lookup_tool(medicine_name: str, active_salts: list) -> dict | str:
#     """
#     Searches the internal medicine CSV database for uses and side effects.
#     It will first search by 'medicine_name', then falls back to 'active_salts'.

#     Args:
#         medicine_name (str): The name of the medicine (can be null).
#         active_salts (list): A list of active salts (can be empty).
#     """
#     # the search will be fuzzy

#     print(f"Medicine DB Lookup activated for: {medicine_name}, {active_salts}")
#     if df_medicines is None or df_medicines.empty:
#         return "Error: Medicine database (medicine_data.csv) is not loaded."

#     # Search by medicine name
#     if medicine_name:
#         name_result = df_medicines[df_medicines['Medicine Name'].str.contains(medicine_name, case=False, na=False)]
#         if not name_result.empty:
#             first_match = name_result.iloc[0]
#             return {
#                 "uses": first_match.get("Uses"),
#                 "side_effects": first_match.get("Side_effects")
#             }

#     # Fallback to searching by active salts
#     if active_salts:
#         for salt in active_salts:
#             # Clean up the salt name (e.g., remove "(500mg)")
#             cleaned_salt = salt.split('(')[0].strip()
#             if not cleaned_salt:
#                 continue
            
#             salt_result = df_medicines[df_medicines['Composition'].str.contains(cleaned_salt, case=False, na=False)]
#             if not salt_result.empty:
#                 first_match = salt_result.iloc[0]
#                 return {
#                     "uses": first_match.get("Uses"),
#                     "side_effects": first_match.get("Side_effects")
#                 }
                
#     return "No information found in the database."