import requests
import folium
from folium import plugins
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
from datetime import datetime

def generate_map():
    base_url = "http://127.0.0.1:8000"
    map_data_response = requests.get(f"{base_url}/listings/map")
    map_data = map_data_response.json()

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
    
    # create dir if it doesn't exist
    os.makedirs("static", exist_ok=True)
    
    # save map with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_path = f"static/map_{timestamp}.html"
    m.save(map_path)
    
    # save latest map reference
    with open("static/latest_map.txt", "w") as f:
        f.write(map_path)

if __name__ == "__main__":
    generate_map()
