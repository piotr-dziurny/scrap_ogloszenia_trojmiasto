from fastapi import FastAPI, Depends, Query
from sqlalchemy import desc, text
from database import get_db

app = FastAPI()

@app.get("/listings", description="Fetch all listings from the database")
def get_listings(db=Depends(get_db)):
    try:
        query = text("SELECT * FROM scraped_items")
        result = db.execute(query)
        listings = result.fetchall()
        return [listing._asdict() for listing in listings]
    except Exception as e:
        return {"Error": str(e)}

@app.get("/listings/cities", description="Fetch unique cities from the database")
def get_cities(db=Depends(get_db)):
    try:
        query = text("SELECT DISTINCT city FROM scraped_items WHERE city is NOT NULL ORDER BY city ASC")
        result = db.execute(query)
        cities = [row[0] for row in result.fetchall()]
        return cities
    except Exception as e:
        return {"Error": str(e)}

@app.get("/listings/map", description="Fetch data required for map visualization")
def get_map_data(db=Depends(get_db)):
    try:
        query = text("""
            SELECT title, latitude, longitude, price, square_meters, rooms, year, url, city, area, price_per_sqr_meter
            FROM scraped_items
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND price IS NOT NULL
            AND square_meters IS NOT NULL AND city IS NOT NULL
        """)
        result = db.execute(query)
        return [row._asdict() for row in result.fetchall()]
    except Exception as e:
        return {"Error": str(e)}


@app.get("/listings/by-cities", description="Fetch data for specific city/cities")
def get_city_data(city: list[str] = Query(None), db=Depends(get_db)):
    try:
        if not city:
            return []
        
        # tuple for SQL 
        cities_tuple = tuple(city)
         
        query = text(f"""
            SELECT title,  price, square_meters, rooms, 
                   year, url, city, area, price_per_sqr_meter
            FROM scraped_items
            WHERE city IN ({",".join([f":city{i}" for i in range(len(cities_tuple))])})
            AND price IS NOT NULL
            AND square_meters IS NOT NULL
        """)
        
        params = {f"city{i}": c for i, c in enumerate(cities_tuple)}
        
        result = db.execute(query, params)
        return [row._asdict() for row in result.fetchall()]
    except Exception as e:
        return {"Error": str(e)}

@app.get("/listings/top-expensive", description="Fetch top 5 most expensive properties")
def get_top_expensive(db=Depends(get_db)):
    try:
        query = text("""
            SELECT city, price, square_meters, rooms, year, area, url
            FROM scraped_items
            WHERE 1=1
                AND title NOT REGEXP 'najem|wynajem|wynajmę|wynajme'
                AND price is NOT NULL
                AND city is not NULL
            ORDER BY price DESC
            LIMIT 5
        """)
        result = db.execute(query)
        return [row._asdict() for row in result.fetchall()]
    except Exception as e:
        return {"Error": str(e)}

@app.get("/listings/top-affordable", description="Fetch top 5 most affordable properties")
def get_top_affordable(db=Depends(get_db)):
    try:
        query = text("""
            SELECT city, price, square_meters, rooms, year, area, url 
            FROM scraped_items
            WHERE 1=1 
                AND title NOT REGEXP 'najem|wynajem|wynajmę|wynajme'
                AND price is NOT NULL
                AND city is not NULL
            ORDER BY price ASC
            LIMIT 5
        """)
        result = db.execute(query)
        return [row._asdict() for row in result.fetchall()]
    except Exception as e:
        return {"Error": str(e)}
