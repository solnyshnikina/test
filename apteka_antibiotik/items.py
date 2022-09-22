# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AptekaAntibiotikItem(scrapy.Item):
    # define the fields for your item here like:
    timestamp = scrapy.Field()
    marketing_tags = scrapy.Field()
    title = scrapy.Field()
    section = scrapy.Field()
    brand = scrapy.Field()
    original = scrapy.Field()
    url = scrapy.Field()

