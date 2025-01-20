import os
import folium

# create dir if it doesn't exist
os.makedirs("static", exist_ok=True)

m = folium.Map(location=[0, 0], zoom_start=2)

default_path = "static/default_map.html"
m.save(default_path)

with open("static/latest_map.txt", "w") as f:
    f.write(default_path)
