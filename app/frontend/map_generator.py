import requests
import folium
from folium import plugins
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
from datetime import datetime

def create_default_map():
    """
    create a default map with no data
    """
    os.makedirs("static", exist_ok=True)
    m = folium.Map(location=[0, 0], zoom_start=2)
    default_path = "static/default_map.html"
    m.save(default_path)
    with open("static/latest_map.txt", "w") as f:
        f.write(default_path)

    return default_path

def create_new_map():
    """
    create a new map with data from the backend
    """
    base_url = "http://backend:8000"
    response = requests.get(f"{base_url}/listings/map")
    map_data = response.json()

    # create map
    m = folium.Map(location=[
        sum(i["latitude"] for i in map_data) / len(map_data),
        sum(i["longitude"] for i in map_data) / len(map_data)
    ], zoom_start=10)

    for row in map_data:
        price_percentile = sum(i["price"] <= row["price"] for i in map_data) / len(map_data)
        normalized_size = (
            (row["square_meters"] - min(i["square_meters"] for i in map_data)) /
            (max(i["square_meters"] for i in map_data) - min(i["square_meters"] for i in map_data))
        )
        color = plt.cm.RdYlGn(1 - price_percentile)
        popup_info = f"""
        Price: {row["price"]:,}<br>
        Square meters: {row["square_meters"]}<br>
        Rooms: {row["rooms"]}<br>
        Year: {row["year"]}<br>
        URL: <a href="{row["url"]}">ogloszenia.trojmiasto.pl</a>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5 + 10 * normalized_size,
            color=mcolors.to_hex(color[:3]),
            fill=True,
            fill_color=mcolors.to_hex(color[:3]),
            fill_opacity=0.7,
            popup=folium.Popup(popup_info, max_width=300)
        ).add_to(m)

    plugins.MiniMap().add_to(m)
    
    # save map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_path = f"static/map_{timestamp}.html"
    m.save(map_path)
    
    # save latest map reference
    with open("static/latest_map.txt", "w") as f:
        f.write(map_path)
