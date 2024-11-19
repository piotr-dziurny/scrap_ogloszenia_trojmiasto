import scrapy
from ogloszenia_trojmiasto import items
import unicodedata

class OgloszeniaSpider(scrapy.Spider):
    name = "ogloszenia"
    allowed_domains = ["ogloszenia.trojmiasto.pl"]
    start_urls = [
        "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-wtorny/mieszkanie/",
        "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-pierwotny/mieszkanie/"
    ]

    def parse(self, response):
        listings = response.css('div.list__item') # main class showing all listings
        for listing in listings:
            relative_url = listing.css("h2.list__item__content__title a::attr(href)").get() # current site
            listing_url = response.urljoin(relative_url)
            yield response.follow(listing_url, callback = self.parse_subsite) # entering subsite

        next_page = response.css("div.pages__controls.pages__controls--right a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback = self.parse)


    def parse_subsite(self, response):
        ogloszenie = items.OgloszenieItem()

        try:
            title = response.css("h1.xogIndex__title::text").get()
        except:
            title = None
        try:
            price = response.css(".xogParams p::text").get()[:-2].strip()
        except:
            price = None
        try:
            rooms = response.css("span:contains('Liczba pokoi') + span::text").get().strip()
        except:
            rooms = None
        try:
            floor = response.css("span:contains('Piętro') + span::text").get().strip()
        except:
            floor = None
        try:
            year = response.css("span:contains('Rok budowy') + span::text").get().strip()
        except:
            year = None
        try:
            price_per_sqr_meter = response.css("span:contains('Cena za m') + span::text").get().strip()
        except:
            price_per_sqr_meter = None
        try:
            square_meters = response.css("span:contains('Pow. nieruchomości') + span::text").get().strip()
        except:
            square_meters = None
        try:
            address = response.css("i.trm.trm-location + span::text").getall()
        except:
            address = None

        ogloszenie["url"] = response.url,
        ogloszenie["title"] = title,
        ogloszenie["price"] = price,
        ogloszenie["rooms"] = rooms,
        ogloszenie["floor"] = floor,
        ogloszenie["year"] = year,
        ogloszenie["price_per_sqr_meter"] = price_per_sqr_meter,
        ogloszenie["square_meters"] = square_meters,
        ogloszenie["address"] = address,
        
        yield ogloszenie