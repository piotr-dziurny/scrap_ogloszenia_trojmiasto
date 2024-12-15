import unicodedata
import logging
from itemadapter import ItemAdapter
from ogloszenia_trojmiasto.geodistance import load_coastline, get_coastline_distance, get_downtown_distances
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

        item["ins_date"] = datetime.today().strftime("%YYYY-%MM-%DD")

        return item

class SyntheticFeaturesPipeline:
    def __init__(self):
        self.coastline = load_coastline() 
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        address = item.get("address")
        if not item:
            self.logger.warning("Item has no address. Skipping distance calcuations")
            return item
        
        # coastline distance
        try:
            item["coastline_distance"] = get_coastline_distance(address, self.coastline)
        except ValueError as e:
            item["coastline_distance"] = None
            self.logger.warning(f"Failed to calculate coastline distance for address '{address}': {e} - setting distance to None.")

        # downtown distances
        try:
            distances = get_downtown_distances(address)
            item["gdynia_downtown_distance"] = distances.get("Gdynia")
            item["gdansk_downtown_distance"] = distances.get("Gdańsk")
            item["sopot_downtown_distance"] = distances.get("Sopot")
        except ValueError as e:
            item["gdynia_downtown_distance"] = None
            item["gdansk_downtown_distance"] = None
            item["sopot_downtown_distance"] = None
            self.logger.warning(f"Failed to calculate downtown distances for address '{address}': {e} - setting distances to None.")

        return item

class DatabasePipeline:
    def __init__(self):
        self.db_helper = DatabaseHelper()

    def process_item(self, item, spider):
        self.db_helper.insert_item(item)
        return item

    def close_spider(self, spider):
        self.db_helper.close()
