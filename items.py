# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArgumentTopicsItem(scrapy.Item):
    topic = scrapy.Field()
    category = scrapy.Field()
    pro_arguments = scrapy.Field()
    con_arguments = scrapy.Field()