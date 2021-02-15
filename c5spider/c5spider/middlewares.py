# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy import exceptions

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import json
from queue import Queue

class C5SpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class C5SpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ProxyPool():
    def __init__(self):
        # 初始化代理池
        self.proxyQueue = Queue()
        self.proxy = None
        with open('./Proxy.json') as json_file:
            proxy_json = json.load(json_file)
            for p in proxy_json:
                ip = p['ip']
                port = p['port']
                self.proxyQueue.put('https://'+ip +':'+port)

    def renewProxyAddr(self):
        # 在地址池中拿去一个代理地址
        self.proxy = self.proxyQueue.get()
        self.proxyQueue.put(self.proxy)

    def getProxyAddr(self):
        return self.proxy

# proxyPool = ProxyPool()

class ProxyPoolString():
    def __init__(self):
        # 初始化代理池
        self.proxyQueue = Queue()
        self.proxy = None
        with open('./Proxy.txt') as proxy_file:
            for l in proxy_file:
                self.proxyQueue.put(l)

    def renewProxyAddr(self):
        # 在地址池中拿去一个代理地址
        self.proxy = self.proxyQueue.get()
        self.proxyQueue.put(self.proxy)

    def getProxyAddr(self):
        return self.proxy

proxyPoolString = ProxyPoolString()

# 给Reqeust加代理middleware
class C5SpiderProxyMiddleware:
    def process_request(self, request, spider):
        # meta key "changeProxy"： 标注是否需要更换proxy
        # meta key "proxy"： proxy地址
        if 'changeProxy' not in request.meta:   # 没有代理的情况，即新请求，添加更换代理flag，重新处理请求
            request.meta['changeProxy'] = True
            return request
        elif request.meta['changeProxy']:       # 需要更换代理情况，更换代理，重新处理请求
            print('更换代理访问' + request.url)
            proxyPoolString.renewProxyAddr()
            request.meta['proxy'] = proxyPoolString.getProxyAddr()
            request.meta['changeProxy'] = False
            # return request
        else:                                   # 不需要更换代理情况，处理请求
            return None
    
    # def process_response(self, request, response, spider):
    #     if 200 <= response.status < 300:                            # 正常情况，返回响应
    #         return response
        # elif response.status == 429 or response.status == 403:      # too many request，需要更换代理
        #     request.meta['changeProxy'] = True
        #     return request
        # else:
        #     raise exceptions.NotSupported(f'Not handled response, res code:{response.status}')

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

# 给Retry换代理middleware
class CustomRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
    
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            #如果返回了[403, 500, 502, 503, 504, 522, 524, 408, 429]这些code，换个proxy试试
            print('更换代理访问(timeout)' + request.url)
            proxyPoolString.renewProxyAddr()
            request.meta['proxy'] = proxyPoolString.getProxyAddr()
            request.meta['changeProxy'] = False

            return self._retry(request, reason, spider) or response
            
        return response
    
    #RetryMiddleware类里有个常量，记录了连接超时那些异常
    #EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
    #                       ConnectionRefusedError, ConnectionDone, ConnectError,
    #                       ConnectionLost, TCPTimedOutError, ResponseFailed,
    #                       IOError, TunnelError)
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            #这里可以写出现异常那些你的处理            
            print('更换代理访问(timeout)' + request.url)
            proxyPoolString.renewProxyAddr()
            request.meta['proxy'] = proxyPoolString.getProxyAddr()
            request.meta['changeProxy'] = False

            return self._retry(request, exception, spider)
    #_retry是RetryMiddleware中的一个私有方法，主要作用是
    #1.对request.meta中的retry_time进行+1 
    #2.将retry_times和max_retry_time进行比较，如果前者小于等于后者，利用copy方法在原来的request上复制一个新request，并更新其retry_times，并将dont_filter设为True来防止因url重复而被过滤。
    #3.记录重试reason