import scrapy

class OgloszeniaSpider(scrapy.Spider):
    name = "listings"
    allowed_domains = ["ogloszenia.trojmiasto.pl"]
    start_urls = [
        "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-wtorny/mieszkanie/"
    ]

    def parse(self, response):
        ogloszenia = response.css('div.list__item') # main class showing all listings

        for ogloszenie in ogloszenia:
            yield{
                "title" : ogloszenie.css('a.list__item__content__title__name::text').get(),
                "price" : ogloszenie.xpath(".//div[contains(@class, 'list__item__picture__price')]/p/text()").get(),
                "url": ogloszenie.css('a.list__item__content__title__name::attr(href)').get()
            }

        next_page = response.css("div.pages__controls.pages__controls--right a::attr(href)").get() # current site
        
        if next_page is not None:
            next_page_url = "https://ogloszenia.trojmiasto.pl/nieruchomosci-rynek-wtorny/mieszkanie/" + next_page
            yield response.follow(next_page_url, callback=self.parse)

# https://docs.scrapy.org/en/latest/intro/tutorial.html#our-first-spider