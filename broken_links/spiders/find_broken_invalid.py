from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class FindBrokenInvalidSpider(CrawlSpider):
    name = "find_broken_invalid"
    allowed_domains = ["scrapebay.com"]
    start_urls = ["https://www.scrapebay.com/"]

    rules = (Rule(LinkExtractor(), callback="parse_item", follow=True),)

    handle_httpstatus_list = [i for i in range(400, 600)]

    def parse_item(self, response):
        if response.status in self.handle_httpstatus_list:
            yield {response.url, response.status}
