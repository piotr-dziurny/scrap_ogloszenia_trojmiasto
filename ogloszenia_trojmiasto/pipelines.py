import unicodedata
import logging
from ogloszenia_trojmiasto.geodistance import load_coastline, get_all_distances 
from ogloszenia_trojmiasto.db_helper import DatabaseHelper
from datetime import datetime

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class CleaningPipeline:
    def process_item(self, item, spider):        
        try:
            item["address"] = unicodedata.normalize("NFKC", "".join(item["address"]).strip())
        except (AttributeError, TypeError, KeyError) as e:
            self.logger.info(f"No adress found in CleaningPipeline: {e}")
            item["address"] = None
        try:
            item["city"] = unicodedata.normalize("NFKC", item["city"])
        except:
            item["city"] = None

        try:
            item["floor"] = 0 if item["floor"] == "Parter" else int(item["floor"])
        except:
            item["floor"] = None

        try:
            item["price"] = float(item["price"][:-2].replace(" ", ""))
        except:
            item["price"] = None

        try:
            item["price_per_sqr_meter"] = float(item["price_per_sqr_meter"].replace(",", "."))
        except:
            item["price_per_sqr_meter"] = None

        try:
            item["rooms"] = int(item["rooms"])
        except:
            item["rooms"] = None

        try:
            item["square_meters"] = float(item["square_meters"].replace(",", "."))
        except:
            item["square_meters"] = None

        try:
            item["year"] = datetime.strptime(item["year"], "%Y")
        except:
            item["year"] = None

        item["created_ts"] = datetime.now()

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
                if item["square_meters"] > 0:  # Avoid division by zero
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
        address = item.get("address")
        if not address:
            self.logger.warning("Item has no address. Skipping geocoding data")
        
        distances = get_all_distances(address or "", self.coastline)
        item.update(distances)
        return item

class DatabasePipeline:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def process_item(self, item, spider):
        url = item["url"]
        
        if url in self.db_helper.get_existing_urls():
            if self.db_helper.is_changed(url, item):
                # data changed - update old record and insert new one
                self.db_helper.update_is_latest(url)
                item["is_latest"] = 1
                self.db_helper.insert_item(item)
                spider.logger.info(f"Data changed for {url} - inserted new row and updated is_latest")
            else:
                # data unchanged - update last_check_ts
                self.db_helper.update_scraped_ts(url)
                spider.logger.info(f"No data change for {url} - updated scraped_ts")
        else:
            # new listing - insert
            item["is_latest"] = 1
            self.db_helper.insert_item(item)
            spider.logger.info(f"New entry for {url} - inserted into database")
            
        return item

    def close_spider(self, spider):
        self.db_helper.close()
