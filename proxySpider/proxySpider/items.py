# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProxyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    num=scrapy.Field() #序列号
    ip=scrapy.Field()
    port=scrapy.Field()
    country=scrapy.Field()