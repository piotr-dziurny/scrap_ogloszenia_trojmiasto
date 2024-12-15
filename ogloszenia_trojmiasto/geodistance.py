from geopy.geocoders import Nominatim
from shapely.geometry import Point
from shapely.ops import nearest_points
import geopandas as gpd
from geographiclib.geodesic import Geodesic
import os

### util functions; distance calculation, converting address to coords, loading geometry of the coastline ###
def get_coordinates(address: str) -> tuple:
    """
    
    get latitude and longitude of an address using Geopy

    """

    geolocator = Nominatim(user_agent="geo_distance")
    location = geolocator.geocode(address)
    if not location:
        raise ValueError("Can't get coordinates: address not found")

    return location.longitude, location.latitude


def calculate_distance(coord1: tuple, coord2: tuple) -> float:
    """
    
    calculate geodesic distance between coordinates using Vincenty's Formula

    https://gis.stackexchange.com/questions/102837/calculated-distance-doesnt-match-google-earth

    """
    geod = Geodesic.WGS84
    result = geod.Inverse(coord1[1], coord1[0], coord2[1], coord2[0])  # lat1, lon1, lat2, lon2
    
    return result["s12"] / 1000 


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

########################

def get_coastline_distance(address: str, coastline) -> float:
    """
    
    calculate the distance from an address to the nearest point on the coastline
    
    """

    # get coordinates of the address:
    address_point = Point(get_coordinates(address))

    # extract goemetries from the coastline MultiLineString:
    line_strings = [line for line in coastline.geoms]
    
    min_distance = float("inf")
    # calculate distance to the nearest point on the coastline:
    for line in line_strings:
        nearest_point = nearest_points(address_point, line)[1]
        distance = calculate_distance(
            (address_point.y, address_point.x), (nearest_point.y, nearest_point.x)
            )

        if distance < min_distance:
            min_distance = distance

    return min_distance


def get_downtown_distances(address: str) -> dict:
    """
    
    calculate the distance from an address to the downtowns of 3city
    
    """

    downtown_coordinates = {
    "Gdańsk": (18.6477211, 54.3495703),
    "Gdynia": (18.5391734, 54.5197073),
    "Sopot": (18.562195548794275, 54.441524799999996)
    }

    try:
        address_coords = get_coordinates(address)
    except:
        raise ValueError(f"Can't calculate distance to downtown: address {address} is not specific enough")
        return None

    gdynia_downtown_coords = downtown_coordinates.get("Gdynia")
    gdansk_downtown_coords = downtown_coordinates.get("Gdańsk")
    sopot_downtown_coords = downtown_coordinates.get("Sopot")

    result = {
        "Gdynia": calculate_distance(address_coords, gdynia_downtown_coords),
        "Gdańsk": calculate_distance(address_coords, gdansk_downtown_coords),
        "Sopot": calculate_distance(address_coords, sopot_downtown_coords)
    }

    return result

if __name__ == "__main__":
    coastline = load_coastline()
    address = "Gdańsk Morena Morenowe Wzgórze"

    try:
        coastline_distance = get_coastline_distance(address, coastline) 
        downtown_distances = get_downtown_distances(address) 
        gdynia_downtown_coords = downtown_distances.get("Gdynia")
        gdansk_downtown_coords = downtown_distances.get("Gdańsk")
        sopot_downtown_coords = downtown_distances.get("Sopot")
        print(f"Distance from {address} to coastline: {coastline_distance:.3f} km\n" \
                f"Distance to downtowns:\n" \
                    f"Gdynia: {gdynia_downtown_coords:.3f} km,\n" \
                    f"Gdańsk: {gdansk_downtown_coords:.3f} km,\n" \
                        f"Sopot: {sopot_downtown_coords:.3f} km")
    except ValueError as e:
        print(f"Error: {e}")
