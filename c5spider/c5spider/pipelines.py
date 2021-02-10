# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import time
from scrapy.exporters import JsonItemExporter
# JsonItemExporter 保存json
# https://blog.csdn.net/qq_27648991/article/details/81514941

class C5SpiderPipeline:
    def __init__(self):
        localtime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        self.file = open(localtime + '-c5items.json', 'wb')  # 必须二进制写入
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        # 开始写入
        self.exporter.start_exporting()

    def open_spider(self, spider):
        print(f'爬虫开始，保存数据到c5items.json')

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        # 完成写入
        self.exporter.finish_exporting()
        self.file.close()
