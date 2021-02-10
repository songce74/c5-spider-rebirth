# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class C5SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # num=scrapy.Field() #序列号
    name=scrapy.Field() #物品名字
    hashName=scrapy.Field() #物品的market hash名字
    price=scrapy.Field() #物品价格
    c5page=scrapy.Field()
    steamPage=scrapy.Field() #steam market页面
    steamLeastSelling=scrapy.Field() #steam market最低售价

