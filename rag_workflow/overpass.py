import requests
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two lat/lon points using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth radius in km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


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
    response = requests.post(url, data={"data": query})
    data = response.json()

    hospitals = []

    for item in data.get("elements", []):
        name = item.get("tags", {}).get("name", "Unknown Hospital")

        # Correct lat/lon for nodes, ways, relations
        if "lat" in item:
            h_lat = item["lat"]
            h_lon = item["lon"]
        else:
            h_lat = item.get("center", {}).get("lat")
            h_lon = item.get("center", {}).get("lon")

        if not h_lat or not h_lon:
            continue

        # Calculate distance
        distance = haversine_distance(lat, lon, h_lat, h_lon)

        hospitals.append({
            "name": name,
            "latitude": h_lat,
            "longitude": h_lon,
            "distance_km": round(distance, 2)
        })

    # Sort by nearest first
    hospitals.sort(key=lambda x: x["distance_km"])

    return hospitals


# 📍 Example: Kurukshetra Coordinates
# 29.9451° N, 76.8173° E
lat = 29.9451
lon = 76.8173

hospitals = find_nearby_hospitals_with_distance(lat, lon, radius=5000)

print(f"Found {len(hospitals)} hospitals:\n")
for h in hospitals:
    print(f"{h['name']} - {h['distance_km']} km away - ({h['latitude']}, {h['longitude']})")


import requests

def geocode_location(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1
    }

    response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    data = response.json()

    if not data:
        return None

    return {
        "latitude": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"]),
        "display_name": data[0]["display_name"]
    }


# Example: convert location name
result = geocode_location("NIT Kurukshetra")
print(result)
