from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ogloszenia_trojmiasto.spiders.ogloszenia import OgloszeniaSpider

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(OgloszeniaSpider)
    process.start()
