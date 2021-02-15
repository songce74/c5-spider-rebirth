from scrapy import cmdline


name = 'C5SpiderDota'
cmd = 'scrapy crawl {0}'.format(name)
cmd += ' -a min_price=200 -a max_price=300'
cmdline.execute(cmd.split())