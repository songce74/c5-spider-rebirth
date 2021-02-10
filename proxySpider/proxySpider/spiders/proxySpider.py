import scrapy
from urllib.parse import unquote # Decode URL
import re
from items import ProxyspiderItem

class ProxySpider(scrapy.Spider):
    name = "proxySpider"
    count_num = 0 # 记录序列号
    test_page = "https://www.google.com/"

    def start_requests(self):
        url = 'http://www.freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(f'已获取一页代理 {response.url}')
        # scrapy.shell.inspect_response(response, self)
        # 爬取代理
        proxy_table = response.xpath('/html/body/div[1]/div[2]/table/tr')
        for item in proxy_table:
            proxyItem = ProxyspiderItem()
            # IP
            ip = item.xpath('td[1]/script/text()').extract_first()
            if ip is not None:
                ip = ip.lstrip("'IPDecode(").rstrip(")'").strip('"')
                ip = unquote(ip)
                ip = re.search(r">\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}<", ip)
                if ip is not None:
                    ip = ip.group().lstrip('>').rstrip('<')
            # Port
            port = item.xpath('td[2]/text()').extract_first()
            # Country
            country = item.xpath('td[5]/text()').extract_first()
            if ip is not None and port is not None and country is not None:
                proxyItem['ip'] = ip
                proxyItem['port'] = port
                proxyItem['country'] = country

                proxy = 'https://' + ip + ':' + port
                yield scrapy.Request(self.test_page, meta={'proxyItem':proxyItem, 'proxy': proxy},\
                     callback=self.validateProxy, dont_filter = True)

        next_page = response.xpath("/html/body/div/div[2]/div[3]/a[contains(text(), 'Next')]/@href").extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def validateProxy(self, response):
        proxyItem = response.request.meta['proxyItem']

        if response.status == 200:
            print(f'成功验证一个代理 {proxyItem["ip"]}:{proxyItem["port"]}')
            proxyItem['num'] = self.count_num
            self.count_num += 1
            yield proxyItem