import unicodedata
import logging

from geopy.geocoders.base import logger
from ogloszenia_trojmiasto.geodistance import load_coastline, get_all_distances 
from ogloszenia_trojmiasto.db_helper import DatabaseHelper
from datetime import datetime

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class CleaningPipeline:
    def process_item(self, item, spider):        
        conversions = {
            "address": lambda x: unicodedata.normalize("NFKC", "".join(x).strip()),
            "city": lambda x: unicodedata.normalize("NFKC", x),
            "floor": lambda x: 0 if x == "Parter" else int(x),
            "price": lambda x: float(x[:-2].replace(" ", "")),
            "price_per_sqr_meter": lambda x: float(x.replace(",", ".")),
            "rooms": int,
            "square_meters": lambda x: float(x.replace(",", ".")),
            "year": lambda x: datetime.strptime(x, "%Y"),
          }
 
        try:
            item["address"] = conversions["address"](item["address"])
        except Exception as e:
            logger.info(f"No address found in {item["url"]}: {e}")
            item["address"] = None
        try:    
            item["city"] = conversions["city"](item["city"]) 
        except Exception as e:
            logger.info(f"No city found in {item["url"]}: {e}") 
            item["city"] = None

        item["created_ts"] = datetime.now()

        for field, converter in conversions.items(): 
            if field in ("address", "city", "created_ts"):
                continue 
            try:
                item[field] = converter(item[field]) if item.get(field) else None
            except Exception:
                item[field] = None

        return item


class PricePipeline:
    """
    some scraped listings have missing price or price per square meter. 
    Pipeline tries to fill in the missing data
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        try:
            # 1. missing price but have price_per_sqr_meter and square_meters
            if item["price"] is None and item["price_per_sqr_meter"] is not None and item["square_meters"] is not None:
                item["price"] = round(item["price_per_sqr_meter"] * item["square_meters"], 2)
                self.logger.info(f"Calculated missing price for {item['url']}")
            
            # 2. missing price_per_sqr_meter but have price and square_meters
            elif item["price_per_sqr_meter"] is None and item["price"] is not None and item["square_meters"] is not None:
                if item["square_meters"] > 0:  # avoid division by zero
                    item["price_per_sqr_meter"] = round(item["price"] / item["square_meters"], 2)
                    self.logger.info(f"Calculated missing price per square meter for {item['url']}")

        except Exception as e:
            self.logger.error(f"Error calculating price data for {item.get("url", "unknown URL")}: {e}")

        return item

class SyntheticFeaturesPipeline:
    def __init__(self):
        self.coastline = load_coastline() 
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        address = item.get("address", None)
        if not address:
            self.logger.warning("Item has no address. Skipping geocoding data")

        distances = get_all_distances(address, self.coastline)
        item.update(distances)
        return item

class DatabasePipeline:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def process_item(self, item, spider):
        url = item["url"]
        
        if url in self.db_helper.get_existing_urls():
            if self.db_helper.is_changed(url, item):
                # data changed - update old record and insert new one:
                self.db_helper.update_is_latest(url) # set old item to is_latest = 0
                item["is_latest"] = 1 # set current item to is_latest = 1
                self.db_helper.insert_item(item)
                spider.logger.info(f"Data changed for {url} - inserted new row and updated is_latest")
            else:
                # data unchanged - update scraped_ts
                self.db_helper.update_scraped_ts(url)
                spider.logger.info(f"No data change for {url} - updated scraped_ts")
        else:
            # new listing - insert and set is_latest = 1
            item["is_latest"] = 1
            self.db_helper.insert_item(item)
            spider.logger.info(f"New entry for {url} - inserted into database")
            
        return item

    def close_spider(self, spider):
        self.db_helper.close()
