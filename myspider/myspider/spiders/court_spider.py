import scrapy
import hashlib

# from myspider.items import MyspiderItem


class CourtSpider(scrapy.spiders.Spider):
    name = "CourtSpider"
    download_delay = 3
    
    allowed_domains = ["court.gov.cn"]
    start_urls = ["http://wenshu.court.gov.cn/",
				  "http://shixin.court.gov.cn/",
				  "http://www.court.gov.cn/"]
    
    url_set = set()
 
    def parse(self, response):
        sel = scrapy.Selector(response)

        current_page_urls = sel.select('//a/@href').extract()

        for url in current_page_urls:
            if url.startswith('http://'):
                pass
            elif url.startswith('/') or url.startswith('.'):
                url = response.urljoin(url)
            else:
                url = '0'

            if url != '0':
                md5_obj = hashlib.md5()
                md5_obj.update(url.encode('utf-8'))
                md5_url = md5_obj.hexdigest()

                if md5_url not in CourtSpider.url_set:
                    CourtSpider.url_set.add(md5_url)
                    yield scrapy.Request(url, callback=self.parse)
