from geopy.geocoders import Nominatim
from shapely.geometry import Point
from shapely.ops import nearest_points
import geopandas as gpd
from geographiclib.geodesic import Geodesic
import os
import time

geolocator = Nominatim(user_agent="geo_distance")
geocoding_cache = {} # store processed data for current scraping session

downtown_coordinates = {
    "Gdańsk": (54.3495703, 18.6477211),
    "Gdynia": (54.5197073, 18.5391734),
    "Sopot": (54.441524799999996, 18.562195548794275)
}

def get_location_data(address: str, retry_count: int = 3) -> dict:
    """
    get geo data with single api call 
    """
    if address in geocoding_cache:
        return geocoding_cache[address]
   
    # type of area to return from API json response
    CITY_AREA_MAPPINGS = {
        "sopot": "quarter",
        "gdynia": "suburb",
        "gdańsk": "suburb"
    }
 
    for attempt in range(retry_count):
        try:
            time.sleep(1) # respect api rate limits 
            location = geolocator.geocode(address, addressdetails=True)
            
            if not location:
                raise ValueError(f"address {address} not found")

            raw_data = location.raw
            address_data = raw_data["address"]
            
            # get district/area based on city name. If city name not in the dict, it's a county town
            area_type = CITY_AREA_MAPPINGS.get(address_data.get("city", "").lower(), "county")
            
            loc = {
                "latitude": float(raw_data["lat"]),
                "longitude": float(raw_data["lon"]),
                "area": address_data.get(area_type, None)
            }
            
            geocoding_cache[address] = loc

            return loc

        except Exception as e:
            if attempt == retry_count - 1:
                raise ValueError(f"failed to geocode address after {retry_count} attempts: {e}")
            time.sleep(5)

def load_coastline():
    """
    load and clip europe's coastline shapefile
    """

    project_root = os.path.dirname(os.path.abspath(__file__))
    coastline_shapefile_path = os.path.join(project_root, "shapefiles", "Europe_coastline_shapefile", "Europe_coastline.shp")
    world_shapefile_path = os.path.join(project_root, "shapefiles", "ne_110m_admin_0_countries", "ne_110m_admin_0_countries.shp")
    country = "Poland"


    # load the world's shapefile and filter it by country name:
    world = gpd.read_file(world_shapefile_path)
    country = world[world["SOVEREIGNT"] == country].dissolve(by="SOVEREIGNT").iloc[0].geometry

    # load europe's coastline shapefile and clip it to include only Poland's coastline:
    coastline = gpd.clip(
        gpd.read_file(coastline_shapefile_path).to_crs("EPSG:4326"),
        country.buffer(0.25)
    ).iloc[0].geometry
    
    return coastline

def calculate_distance(coord1: tuple, coord2: tuple) -> float:
    """
    calculate geodesic distance between coordinates using Vincenty's Formula
    
    coordinates in format (latitude, longitude)

    https://gis.stackexchange.com/questions/102837/calculated-distance-doesnt-match-google-earth
    https://geographiclib.sourceforge.io/html/python/code.html
    """
    geod = Geodesic.WGS84
    result = geod.Inverse(coord1[0], coord1[1], coord2[0], coord2[1])  # Inverse(lat1: float, lon1: float, lat2: float, lon2: float)
    
    return result["s12"] / 1000 # return distance in kilometers

def calculate_coastline_distance(address_point: Point, coastline) -> float:
    """
    calculate the distance from an address to the nearest point on the coastline
    """
    min_distance = float("inf")
    # calculate distance to the nearest point on the coastline:
    for line in coastline.geoms:
        nearest_point = nearest_points(address_point, line)[1]
        distance = calculate_distance(
            (address_point.y, address_point.x), (nearest_point.y, nearest_point.x)
            )

        if distance < min_distance:
            min_distance = distance

    return min_distance

def get_all_distances(address: str, coastline) -> dict:
    """
    calculate distances to coastline and downtowns and return adressess district/area/county
    """
    try:
        loc_data = get_location_data(address)
        lon, lat = loc_data["longitude"], loc_data["latitude"]
        point = Point(lon, lat)

        # calculate coastline distance
        coastline_distance = calculate_coastline_distance(point, coastline)

        # calculate downtown distances
        downtown_distances = {
            city: calculate_distance((lat, lon), coords)
            for city, coords in downtown_coordinates.items()
        }

        return {
            "coastline_distance": coastline_distance,
            "gdynia_downtown_distance": downtown_distances["Gdynia"],
            "gdansk_downtown_distance": downtown_distances["Gdańsk"],
            "sopot_downtown_distance": downtown_distances["Sopot"],
            "area": loc_data["area"],
            "coords": f"{lat}, {lon}"
        }

    except ValueError:
        return {
            "coastline_distance": None,
            "gdynia_downtown_distance": None,
            "gdansk_downtown_distance": None, 
            "sopot_downtown_distance": None,
            "area": None,
            "coords": None
        }

if __name__ == "__main__":
    coastline = load_coastline()
    addresses = {
        "test": "alksdaksjhd",
        "sopot": "Sopot Górny Sopot 23 Marca 73",
        "gdynia": "Gdynia Śródmieście Świętojańska 39",
        "gdańsk": "Gdańsk Wrzeszcz Górny de Gaulle",
        "reda":  "Reda Marii Konopnickiej"
    }

    for ad in addresses:
        result = get_all_distances(addresses[ad], coastline)
        print(result)
