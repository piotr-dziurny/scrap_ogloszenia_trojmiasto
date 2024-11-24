## Simple scraper for ogloszenia.trojmiasto.pl

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

---

### Synthetic Features
In addition to the scraped data, the scraper calculates the following synthetic features:

- **coastline_distance**: distance from the apartment to the nearest point on the coastline
- **gdynia_downtown_distance**: distance from the apartment to the downtown of Gdynia
- **gdansk_downtown_distance**: distance from the apartment to the downtown of Gdańsk
- **sopot_downtown_distance**: distance from the apartment to the downtown of Sopot


### Sources
* https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
* https://www.eea.europa.eu/data-and-maps/data/eea-coastline-for-analysis-1/gis-data/europe-coastline-shapefile