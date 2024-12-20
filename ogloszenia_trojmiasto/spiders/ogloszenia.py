import scrapy
from ogloszenia_trojmiasto.settings import DATABASE 
from ogloszenia_trojmiasto import items
from ogloszenia_trojmiasto.db_helper import DatabaseHelper
import os
import logging

class OgloszeniaSpider(scrapy.Spider):
    name = "ogloszenia"
    allowed_domains = ["ogloszenia.trojmiasto.pl"]
    start_urls = [
        "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-wtorny/mieszkanie/",
        "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-pierwotny/mieszkanie/"
    ]
    
    def __init__(self):
        super().__init__()
        if DATABASE:
            self.db_helper = DatabaseHelper()
            self.existing_urls = set(self.db_helper.get_existing_urls())
            self.logger.info(f"Fetched {len(self.existing_urls)} urls from the database")
        else:
            self.db_helper = None
            self.existing_urls = set()

    def parse(self, response):
        listings = response.css('div.list__item') # main class showing all listings
        for listing in listings:
            relative_url = listing.css("h2.list__item__content__title a::attr(href)").get() # current site
            listing_url = response.urljoin(relative_url)

            if DATABASE and listing_url in self.existing_urls: # check if listing is in already in db
                self.logger.info(f"skipping {listing_url}")
                continue

            yield response.follow(listing_url, callback = self.parse_subsite) # enter subsite

        next_page = response.css("div.pages__controls.pages__controls--right a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback = self.parse)


    def parse_subsite(self, response):
        ogloszenie = items.OgloszenieItem()

        fields = {
            "title": "h1.xogIndex__title::text",
            "price": ".xogParams p::text",
            "rooms": "span:contains('Liczba pokoi') + span::text",
            "floor": "span:contains('Piętro') + span::text",
            "year": "span:contains('Rok budowy') + span::text",
            "price_per_sqr_meter": "span:contains('Cena za m') + span::text",
            "square_meters": "span:contains('Pow. nieruchomości') + span::text",
            "address": "i.trm.trm-location + span::text",
        }

        for field, selector in fields.items():
            try:
                if field == "address":
                    value = response.css(selector).getall() # use getall(); address is split across multiple elements
                    ogloszenie[field] = value
                else:
                    value = response.css(selector).get()
                    ogloszenie[field] = value.strip() if value else None # strip result for readbility
            except Exception as e:
                self.logger.error(f"Error extracting {field}: {e}")
                ogloszenie[field] = None

        ogloszenie["url"] = response.url

        yield ogloszenie
