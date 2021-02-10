import scrapy
import json 
from items import C5SpiderItem
from queue import Queue

class C5SpiderDota(scrapy.Spider):
    name = "C5SpiderDota"
    host = "https://www.c5game.com/"
    allowed_domains = ['c5game.com', 'steamcommunity.com', 'steam.com']
    username = "411379040"            # 帐号
    password = "Songce1995111"          # 密码
    headerData = {
        "Referer": "https://www.google.com/",
        "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,en-GB;q=0.6",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    handle_httpstatus_list = [429,403]

    # 第一步：访问登录页面
    def start_requests(self):
        c5MainPage = "https://www.c5game.com/"
        loginIndexReq = scrapy.Request(
            url = c5MainPage,
            headers = self.headerData,
            callback = self.parseLoginPage,
            dont_filter = True,     # 防止页面因为重复爬取，被过滤了
            meta = {'changeProxy': False}
        )
        yield loginIndexReq

    # 第二步：分析登录页面，取出必要的参数，然后发起登录请求POST
    def parseLoginPage(self, response):
        loginPostUrl = "https://www.c5game.com/api/login/login"
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url = loginPostUrl,
            headers = self.headerData,
            method = "POST",
            meta = {'changeProxy': False},
            # post的具体数据
            formdata = {
                "LoginForm[username]": self.username,
                "LoginForm[password]": self.password,
                "LoginForm[rememberMe]": '1',
                "LoginForm[loginType]": '1'

                # "other": "other",
            },
            callback = self.loginResParse,
            dont_filter = True,
        )

    # 第三步：分析登录结果，成功便开始爬取
    def loginResParse(self, response):
        self.log(f'检查是否登录成功')
        
        if json.loads(response.text)['message']  == "登录成功":
            self.log('登录成功!')
            url = 'https://www.c5game.com/dota.html?'
            min_price = getattr(self, 'min_price', None)
            max_price = getattr(self, 'max_price', None)
            if min_price is not None:
                url += f'min={min_price}&'
            if max_price is not None:
                url += f'max={max_price}&'
            
            yield scrapy.Request(url=url, callback=self.parse, meta = {'changeProxy': False})
        else:
            self.log('登录失败')

    def parse(self, response):
        self.log(f'解析 {response.url}')
        item_list = response.xpath('//*[@id="yw0"]/div/ul/li')
        for item in item_list:
            c5_item = C5SpiderItem()
            c5_item['name'] = item.xpath('.//p[1]/a/span/text()').extract_first()
            # 这里获取的是人民币
            c5_item['price'] = item.xpath('.//p[2]/span[1]/span/text()').extract_first().replace('￥', '').strip()
            # 进入单个物品页面
            c5itemPageUrl = item.xpath('.//a/@href').extract_first()
            c5itemPageUrl = response.urljoin(c5itemPageUrl)
            c5_item['c5page'] = c5itemPageUrl
            yield scrapy.Request(c5itemPageUrl, meta={'c5_item':c5_item, 'changeProxy': False}, callback=self.c5ItemParse)

        # 获取下一页地址
        # next_page = response.xpath("//li[@class='next']/a/@href").extract_first()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)

    def c5ItemParse(self,response):
        c5_item = response.request.meta['c5_item']
        # scrapy.shell.inspect_response(response, self)
        market_hash_name = response.xpath('//*[@id="content"]/div[3]/div[2]/div[1]/div[3]/div/a/@href').extract_first()
        if market_hash_name is not None:
            # 获取Steam价格数据
            c5_item['steamPage'] = market_hash_name
            market_hash_name = market_hash_name.split('/')[-1]
            c5_item['hashName'] = market_hash_name
            appid, currency = 570, 23
            steamLookupPage = 'https://steamcommunity.com/market/priceoverview/?' +\
                        f'appid={appid}&' + f'currency={currency}&' +\
                        f'market_hash_name={market_hash_name}'
            yield scrapy.Request(steamLookupPage, meta={'c5_item':c5_item, 'changeProxy': True}, \
                     callback=self.steamPriceParse, dont_filter = True)

    def steamPriceParse(self, response):
        # 从steam api里面提取最低售价
        # 请求太多会触发 429 Too Many Requests
        c5_item = response.request.meta['c5_item']
        res = response.text
        lowest_price = json.loads(res)['lowest_price']
        c5_item['steamLeastSelling'] = lowest_price.replace('¥', '').strip() #最低售价
        yield c5_item