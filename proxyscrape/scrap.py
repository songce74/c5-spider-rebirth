import proxyscrape
import time

collector = proxyscrape.create_collector('default', 'http')  # Create a collector for http resources
proxies = collector.get_proxies()  # Retrieve a united states proxy
localtime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
with open(localtime + '-proxy.txt', 'w')  as proxy_file:
    for p in proxies:
        proxy_file.write(p.type+ '://' + p.host + ':' + p.port +'\n')