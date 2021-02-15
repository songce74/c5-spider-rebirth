import json
import ast

class PriceAnalyzer():
    def __init__(self, filename):
        #  encoding="utf-8"
        with open(filename, encoding="utf-8") as price_file:
            f = price_file.read().replace('\n', '')
            self.price_list = json.loads(f)
            # self.price_list = ast.literal_eval(price_file)
            
    
    def analyze(self):
        self.result_hash_name_list = []
        num = 0
        for item in self.price_list:
            hash_name = item['hashName']
            cn_price = float(item['price'])
            steam_price = item['steamLeastSelling'].replace(',', '')
            steam_price = float(steam_price)
            # c5page = item['c5page']
            # steam_marker_page = item['steamPage']
            price_ratio = cn_price / (steam_price/1.15)
            self.result_hash_name_list.append({'num': num,'hash_name': hash_name, 'ratio': price_ratio})
            num += 1

        self.sorted_result = sorted(self.result_hash_name_list, key = lambda x:x['ratio'])

    def getNumResult(self, num):
        for item in self.sorted_result[:num]:
            output_item = self.price_list[item['num']]
            print(f"物品：{output_item['name']} 平台售价：{output_item['price']} 比例：{item['ratio']:.2f} 链接：{output_item['c5page']}")

analyzer = PriceAnalyzer('2021-02-11-11-43-29-c5items.json')
analyzer.analyze()
analyzer.getNumResult(10)


