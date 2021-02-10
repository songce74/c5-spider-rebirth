from scrapy import cmdline


name = 'C5SpiderDota'
cmd = 'scrapy crawl {0}'.format(name)
cmd += ' -a min_price=100 -a max_price=200'
cmdline.execute(cmd.split())