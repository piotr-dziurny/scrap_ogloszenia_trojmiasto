import unicodedata
import logging
from itemadapter import ItemAdapter
from ogloszenia_trojmiasto.geodistance import CoastlineDistance, DowntownDistance
from datetime import datetime

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class RemoveTuplePipeline:
    def process_item(self, item, spider):
        item["address"] = "".join(item["address"][0])
        item["floor"] = item["floor"][0]
        item["price"] = item["price"][0]
        item["price_per_sqr_meter"] = item["price_per_sqr_meter"][0]
        item["rooms"] = item["rooms"][0]
        item["square_meters"] = item["square_meters"][0]
        item["title"] = item["title"][0]
        item["url"] = item["url"][0]
        item["year"] = item["year"][0]

        return item

class CleaningPipeline:
    def process_item(self, item, spider):
        item["address"] = unicodedata.normalize("NFKC", item["address"])
        item["floor"] = 0 if item["floor"] == "Parter" else int(item["floor"])
        item["price"] = float(item["price"].replace(" ", ""))
        item["price_per_sqr_meter"] = float(item["price_per_sqr_meter"].replace(",", "."))
        item["rooms"] = int(item["rooms"])
        item["square_meters"] = float(item["square_meters"].replace(",", "."))
        item["year"] = datetime.strptime(item["year"], "%Y")

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
            self.logger.error(f"Failed to calculate coastline distance for address '{item['address']}': {e} - setting distance to None.")

        try:
            distances = self.downtown_calculator.get_distance(item["address"])
            item["gdynia_downtown_distance"] = distances.get("Gdynia")
            item["gdansk_downtown_distance"] = distances.get("Gdańsk")
            item["sopot_downtown_distance"] = distances.get("Sopot")
        except ValueError as e:
            item["gdynia_downtown_distance"] = None
            item["gdansk_downtown_distance"] = None
            item["sopot_downtown_distance"] = None
            self.logger.error(f"Failed to calculate downtown distances for address '{item['address']}': {e} - setting distances to None.")

        return item