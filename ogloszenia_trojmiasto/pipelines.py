import unicodedata
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class OgloszeniaTrojmiastoPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name == "address":
                # decoding address:
                value = adapter.get(field_name)
                adapter[field_name] = unicodedata.normalize("NFKD", "".join(value[0])) # list inside of tuple
            elif field_name == "coastline_distnace":
                value = adapter.get(field_name)
                pass
                #adapter[field_name] = get_distance(value)
            elif field_name == "downtown_distance":
                value = adapter.get(field_name)
                #adapter[field_name] = get_distance(value)
                pass

        return item