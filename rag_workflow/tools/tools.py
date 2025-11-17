from langchain_core.tools import tool 
from langchain_tavily import TavilySearch
import os
import math
import requests

from dotenv import load_dotenv

load_dotenv()



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
def find_nearby_hospitals_with_distance(lat, lon, radius=5000):
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
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
        distance = haversine_distance(lat, lon, h_lat, h_lon)

        hospitals.append({
            "name": name,
            "distance_km": round(distance, 2)
        })

    # Sort by nearest first
    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals
# ...existing code...
@tool
def find_nearby_hospitals(place_name):
    """use this function to find nearby hospitals."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return []

    if not data:
        return []

    try:
        latitude = float(data[0]["lat"])
        longitude = float(data[0]["lon"])
    except (KeyError, TypeError, ValueError):
        return []

    hospitals = find_nearby_hospitals_with_distance(lat=latitude, lon=longitude, radius=5000)
    return hospitals
# ...existing code...