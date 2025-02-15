import requests
from dash import Dash, Input, Output, html, dcc, dash_table
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
from flask import Response
from dash.dash_table.Format import Format
from map_utils import get_latest_map_path
import time

app = Dash(__name__)

@app.server.route("/status")
def status_check():
    return Response(status=200)

map_path = get_latest_map_path()

base_url = "http://backend:8000"

while len(requests.get(f"{base_url}/listings").json()) < 5:
    time.sleep(5)

cities_data = []  # empty list before first data update

app.layout = html.Div([
    html.H1("Trójmiasto listings"),

    # embed map 
    html.Div([
        html.Iframe(
            id="map-iframe",
            src=map_path,
            width="100%",
            height="680px"
        )
    ], className="mb-4"),

    # interval component to trigger updates of embedded html map
    dcc.Interval(
        id="map-update",
        interval=60 * 1000 * 60, # check for new map every hour (n_intervals +=1)
        n_intervals=0 # number of times the interval has passed
    ),

    # city filter
    html.Div([
        dcc.Dropdown(
            options=[{"label": str(city), "value": str(city)} for city in cities_data],
            id="city-dropdown",
            multi=True,
            placeholder="Select cities..."
        )
    ], className="mb-4"),

    # graphs in grid layout
    html.Div(
        style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gap": "20px", "padding": "20px"},
        children=[
            dcc.Graph(id="price-hist-1", style={"height": "500px"}),
            dcc.Graph(id="price-hist-2", style={"height": "500px"}),
            dcc.Graph(id="room-count-bar", style={"height": "500px"}),
            dcc.Graph(id="city-bar", style={"height": "500px"})
        ]
    ),
    
    # grid layout for "top" properties tables 
    html.Div(
        style={"display": "flex", "gap": "20px", "padding": "20px"},
        children=[
            # left side: most expensive properties
            html.Div(style={"flex": "1"}, children=[
                html.H2("Most expensive properties"),
                dash_table.DataTable(
                    id="top-expensive-table",
                    data=[],
                    columns=[
                        {"name": "City", "id": "city"},
                        {"name": "Price (PLN)", "id": "price", "type": "numeric", "format": Format(group=True)},
                        {"name": "Square Meters", "id": "square_meters", "type": "numeric", "format": Format(group=True)},
                        {"name": "Rooms", "id": "rooms", "type": "numeric", "format": Format(group=True)},
                        {"name": "Year", "id": "year"},
                        {"name": "Area", "id": "area"},
                        {"name": "URL", "id": "url", "presentation": "markdown"}
                    ],
                    style_cell={"whiteSpace": "normal", "height": "auto", "textAlign": "center"},
                    style_header={"textAlign": "center"},
                )
            ]),

            # right side: most affordable properties
            html.Div(style={"flex": "1"}, children=[
                html.H2("Most affordable properties"),
                dash_table.DataTable(
                    id="top-affordable-table",
                    data=[],
                    columns=[
                        {"name": "City", "id": "city"},
                        {"name": "Price (PLN)", "id": "price", "type": "numeric", "format": Format(group=True)},
                        {"name": "Square Meters", "id": "square_meters", "type": "numeric", "format": Format(group=True)},
                        {"name": "Rooms", "id": "rooms", "type": "numeric", "format": Format(group=True)},
                        {"name": "Year", "id": "year"},
                        {"name": "Area", "id": "area"},
                        {"name": "URL", "id": "url", "presentation": "markdown"}
                    ],
                    style_cell={"whiteSpace": "normal", "height": "auto", "textAlign": "center"},
                    style_header={"textAlign": "center"},
                )
            ]),
        ]
    ),
    # interval component for tables updates 
    dcc.Interval(
        id="table-update",
        interval=60*1000,  # update every minute 
        n_intervals=0
    )
], style={"margin-left": "240px", "margin-right": "240px"})


# callback to update the map 
@app.callback(Output("map-iframe", "src"),
              Input("map-update", "n_intervals"))
def update_map(n):
    return get_latest_map_path()

# callback to update the graphs based on selected cities
@app.callback(
    [
        Output("price-hist-1", "figure"),
        Output("price-hist-2", "figure"),
        Output("room-count-bar", "figure"),
        Output("city-bar", "figure")
    ],
    [Input("city-dropdown", "value")]
)
def update_graphs(selected_cities):
    # if no city is selected return empty plots
    if not selected_cities:
        empty_fig = {} 
        return empty_fig, empty_fig, empty_fig, empty_fig

    by_cities = f"{base_url}/listings/by-cities"
    city_params = "&".join([f"city={city}" for city in selected_cities])
    query_url = f"{by_cities}?{city_params}"

    # fetch data from API
    response = requests.get(query_url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch data from the API")

    data = pd.DataFrame(response.json()) 

    # hist 1: Price < 3M
    filtered_price_1 = data[data["price"] < 3_000_000]
    price_hist_1 = px.histogram(
        filtered_price_1, 
        x="price",
        nbins=100,
        title="Price distribution (< 3M PLN)",
        labels={"price": "Price (PLN)"},
        color_discrete_sequence=["skyblue"],
        height=500
    )
    price_hist_1.update_layout(
        margin=dict(t=30, l=30, r=30, b=30),
        xaxis_title="Price (PLN)",
        yaxis_title="Number of properties"
    )

    # hist 2: Price >= 3M
    filtered_price_2 = data[data["price"] >= 3_000_000]
    price_hist_2 = px.histogram(
        filtered_price_2, 
        x="price", 
        nbins=100,
        title="Price distribution (≥ 3M PLN)",
        labels={"price": "Price (PLN)"},
        color_discrete_sequence=["skyblue"],
        height=500
    )
    price_hist_2.update_layout(
        margin=dict(t=30, l=30, r=30, b=30),
        xaxis_title="Price (PLN)",
        yaxis_title="Number of properties"
    )

    # barplot rooms:
    temp_df = data.copy()

    def categorize_rooms(x):
        if pd.notnull(x):
            return str(x) if x < 6 else "6+"
        return "no data"

    temp_df["room_group"] = temp_df["rooms"].apply(categorize_rooms)
    
    room_counts = temp_df["room_group"].value_counts().sort_index().reset_index()
    room_counts.columns = ["Number of rooms", "Number of listings"]
    room_count_bar = px.bar(
        room_counts,
        x="Number of rooms",
        y="Number of listings",
        title="Number of listings by room count",
        color_discrete_sequence=["orange"],
        height=500
    )
    room_count_bar.update_layout(
        margin=dict(t=30, l=30, r=30, b=30)
    )

    # avg prices plot:
    city_counts = data["city"].value_counts()
    valid_cities = city_counts[city_counts >= 1].index # only include cities with 1 or more listings
    filtered_city_data = data[data["city"].isin(valid_cities)]
    city_comparison = filtered_city_data.groupby("city").agg(
        median_price=("price", "median"),
        median_price_per_sqr=("price_per_sqr_meter", "median"),
        count=("price", "count")
    ).reset_index()
    city_bar = px.bar(
        city_comparison, 
        x="city", 
        y=["median_price", "median_price_per_sqr"],
        title="Median price/price per square meter by city",
        labels={"value": "PLN", "variable": "Metric"},
        barmode="group",
        text="count",
        height=500
    )
    city_bar.update_layout(
        margin=dict(t=30, l=30, r=30, b=30)
    )

    return price_hist_1, price_hist_2, room_count_bar, city_bar

# callback to update city dropdown
@app.callback(
    Output("city-dropdown", "options"),
    [Input("table-update", "n_intervals")]
)
def update_city_dropdown(n):
    # fetch unique cities for filtering
    unique_cities = requests.get(f"{base_url}/listings/cities").json()
    return [{"label": str(city), "value": str(city)} for city in unique_cities]

# callback to update tables and city dropdown
@app.callback(
    [
        Output("top-expensive-table", "data"),
        Output("top-affordable-table", "data")
    ],
    [Input("table-update", "n_intervals")]
)
def update_tables(n):
    # fetch top expensive properties from backend
    top_expensive_response = requests.get(f"{base_url}/listings/top-expensive")
    top_expensive = pd.DataFrame(top_expensive_response.json())
    # creating hyperlinks in markdown (dash doesn't support html hyperlinks) 
    top_expensive["url"] = top_expensive["url"].apply(lambda x: f"[Click](<{x}>)")

    # fetch top affordable properties from backend
    top_affordable_response = requests.get(f"{base_url}/listings/top-affordable") 
    top_affordable = pd.DataFrame(top_affordable_response.json())
    # creating hyperlinks in markdown (dash doesn't support html hyperlinks) 
    top_affordable["url"] = top_affordable["url"].apply(lambda x: f"[Click](<{x}>)")

    return (
        top_expensive.to_dict("records"), 
        top_affordable.to_dict("records")
    )
