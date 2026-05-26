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
import math
import requests
from typing import List, Dict

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """Calculate distance in kilometers."""
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


def find_nearby_hospitals_with_distance(lat, lon, radius: int = 5000) -> List[Dict]:
    """Main function to fetch nearby hospitals."""
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        print(f"Invalid coordinates: {lat}, {lon}")
        return []

    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    
    headers = {
        'User-Agent': 'HospitalFinderApp/1.0 (Grok Assisted - chetan@hisar)',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    try:
        response = requests.post(url, headers=headers, data={'data': query}, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error {response.status_code}: {e}")
        if hasattr(response, 'text'):
            print("Response:", response.text[:400])
        return []
    except Exception as e:
        print(f"Error fetching hospitals: {e}")
        return []

    hospitals = []
    for item in data.get("elements", []):
        tags = item.get("tags", {})
        name = tags.get("name", "Unknown Hospital")

        if "lat" in item and "lon" in item:
            h_lat = item["lat"]
            h_lon = item["lon"]
        else:
            center = item.get("center") or {}
            h_lat = center.get("lat")
            h_lon = center.get("lon")

        if h_lat is None or h_lon is None:
            continue

        try:
            h_lat = float(h_lat)
            h_lon = float(h_lon)
            distance = haversine_distance(lat, lon, h_lat, h_lon)
            
            hospitals.append({
                "name": name,
                "distance_km": round(distance, 2),
                "lat": round(h_lat, 6),
                "lon": round(h_lon, 6),
            })
        except Exception:
            continue

    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals


@tool
def find_nearby_hospitals(lat: str, long: str):
    """Use this tool to find nearby hospitals."""
    hospitals = find_nearby_hospitals_with_distance(lat=lat, lon=long, radius=5000)
    # print(f"Found {len(hospitals)} hospitals")
    return hospitals
