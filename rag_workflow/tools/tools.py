import os
import json
import math
import requests
# import PIL.Image

from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_tavily import TavilySearch


load_dotenv()


##################### search tool ############################

tavily_search = TavilySearch(max_results=3)

@tool
def search(query: str) -> str:
    """Takes a query and perform web search"""
    print("search tool active")
    res = tavily_search.invoke(query)

    # print("res of search", res)

    l = ""
    flag = res.get("results", None)
    if flag:
        for i in res["results"]:
            l = l + i["content"]

        l = l[:500]

        # print(l)
    return l



######################3 find nearby hospitals ######################

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

def find_nearby_hospitals_with_distance(lat, long, radius=5000):
    try:
        lat = float(lat)
        long = float(long)
    except Exception as e:
        print(f"invalid coordinated provided: {lat}, {long}")
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

    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals


@tool
def find_nearby_hospitals(lat: str , long: str):
    """ use this tool to find nearby hospitals."""

    hospitals = find_nearby_hospitals_with_distance(lat=lat, long=long, radius=5000)

    print("hospitals", hospitals)

    return hospitals