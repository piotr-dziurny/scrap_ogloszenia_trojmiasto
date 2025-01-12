project structure:

```
.
├── app
│   ├── backend
│   │   ├── database.py
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   └── frontend
│       ├── app.py
│       ├── assets
│       │   └── style.css
│       ├── Dockerfile
│       ├── map_generator.py
│       ├── requirements.txt
│       └── static
│           ├── latest_map.txt
│           └── map_20250112_170431.html
├── db
│   ├── Dockerfile
│   └── init.sql
├── docker-compose.yml
├── README.md
└── scraper
    ├── Dockerfile
    ├── ogloszenia_trojmiasto
    │   ├── db_helper.py
    │   ├── geodistance.py
    │   ├── items.py
    │   ├── middlewares.py
    │   ├── pipelines.py
    │   ├── settings.py
    │   ├── shapefiles
    │   │   ├── Europe_coastline_shapefile
    │   │   └── ne_110m_admin_0_countries
    │   └── spiders
    │       └── ogloszenia.py
    ├── requirements.txt
    ├── run_spider.py
    └── scrapy.cfg
```
