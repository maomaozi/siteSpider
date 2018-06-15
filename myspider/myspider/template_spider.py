import scrapy
import hashlib

class %s(scrapy.spiders.Spider):
    name = "%s"
    download_delay = %d

    allowed_domains = ["%s"]
    start_urls = ["%s"]

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

                if md5_url not in %s.url_set:
                    %s.url_set.add(md5_url)
                    yield scrapy.Request(url, callback=self.parse)
