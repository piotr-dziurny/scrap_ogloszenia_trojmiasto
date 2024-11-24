import unicodedata
import logging
from itemadapter import ItemAdapter
from ogloszenia_trojmiasto.geodistance import CoastlineDistance, DowntownDistance
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
        except:
            item["address"] = None

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

        return item

class SyntheticFeaturesPipeline:
    def __init__(self):
        self.coastline_calculator = CoastlineDistance()
        self.downtown_calculator = DowntownDistance()
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        try:
            item["coastline_distance"] = self.coastline_calculator.get_distance(item["address"])
        except ValueError as e:
            item["coastline_distance"] = None
            self.logger.warning(f"Failed to calculate coastline distance for address '{item['address']}': {e} - setting distance to None.")

        try:
            distances = self.downtown_calculator.get_distance(item["address"])
            item["gdynia_downtown_distance"] = distances.get("Gdynia")
            item["gdansk_downtown_distance"] = distances.get("Gdańsk")
            item["sopot_downtown_distance"] = distances.get("Sopot")
        except ValueError as e:
            item["gdynia_downtown_distance"] = None
            item["gdansk_downtown_distance"] = None
            item["sopot_downtown_distance"] = None
            self.logger.warning(f"Failed to calculate downtown distances for address '{item['address']}': {e} - setting distances to None.")

        return item

class DatabasePipeline:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def process_item(self, item, spider):
        self.db_helper.insert_item(item)
        return item

    def close_spider(self, spider):
        self.db_helper.close()