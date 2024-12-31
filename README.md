The scraped data consists of apartments from the "rynek pierwotny" and "rynek wtórny" categories.

### Scraped data

- **url**: URL of the listing
- **title**: title of the listing
- **price**: price of the apartment
- **rooms**: number of rooms in the apartment
- **floor**: floor on which the apartment is located
- **year**: year the building was constructed
- **price per square meters**: price per square meter of the apartment
- **square meters**: total area of the apartment in square meters
- **address**: address of the apartment
- **city/town**: city or town in which the apartment is located
---

### Synthetic Features
In addition to the scraped data, the scraper calculates the following synthetic features:

- **coastline_distance**: distance from the apartment to the nearest point on the coastline
- **gdynia_downtown_distance**: distance from the apartment to the downtown of Gdynia
- **gdansk_downtown_distance**: distance from the apartment to the downtown of Gdańsk
- **sopot_downtown_distance**: distance from the apartment to the downtown of Sopot
- **area**: district or county in which the apartment is located
---

### Instructions

1. Clone the repo
2. Create and activate virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```
---

#### Database integration
Requirements:
>  * an existing MySQL database instance
>  * database credentials specified in a `.env` file

* By default, database integration is disabled (set as `DATABASE=False` in settings.py).
* Before running the scraper with database integration, run the following command to create necessary table:
```
python3 db_helper.py
```

---

#### Scraper run examples:
1. save to CSV and store in database:
```
scrapy crawl ogloszenia -o data.csv
```
2. store in database only:

```
scrapy crawl ogloszenia
```
---
### Sources
* https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
* https://www.eea.europa.eu/data-and-maps/data/eea-coastline-for-analysis-1/gis-data/europe-coastline-shapefile
