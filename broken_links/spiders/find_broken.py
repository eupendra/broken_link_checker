from urllib.parse import urlparse

import scrapy
from scraper_helper import headers, run_spider
from twisted.internet.error import DNSLookupError

START_PAGE = 'https://www.scrapebay.com'


def is_valid_url(url):
    try:
        result = urlparse(url.strip())
        return all([result.scheme, result.netloc])
    except:
        return False


def follow_this_domain(link):
    return urlparse(link.strip()).netloc == urlparse(START_PAGE).netloc


class FindBrokenSpider(scrapy.Spider):
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': headers(),
        'ROBOTSTXT_OBEY': False,
        'RETRY_TIMES': 1
    }
    name = "find_broken"

    handle_httpstatus_list = [i for i in range(400, 600)]

    def start_requests(self):
        yield scrapy.Request(START_PAGE, cb_kwargs={
            'source': 'NA',
            'text': 'NA'
        }, errback=self.handle_error)

    def parse(self, response, source, text):
        if response.status in self.handle_httpstatus_list:
            item = dict()
            item["Source_Page"] = source
            item["Link_Text"] = text
            item["Broken_Page_Link"] = response.url
            item["HTTP_Code"] = response.status
            item["External"] = not follow_this_domain(response.url)
            yield item
            return  # do not process further for non-200 status codes

        content_type = response.headers.get("content-type", "").lower()
        self.logger.debug(f'Content type of {response.url} is f{content_type}')
        if b'text' not in content_type:
            self.logger.info(f'{response.url} is NOT HTML')
            return  # do not process further if not HTML

        for a in response.xpath('//a'):
            text = a.xpath('./text()').get()
            link = response.urljoin(a.xpath('./@href').get())
            if not is_valid_url(link):
                return
            if follow_this_domain(link):
                yield scrapy.Request(link, cb_kwargs={
                    'source': response.url,
                    'text': text
                },errback=self.handle_error)
            else:
                yield scrapy.Request(link, cb_kwargs={
                    'source': response.url,
                    'text': text
                }, callback=self.parse_external, errback=self.handle_error)

    def handle_error(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        request = failure.request
        self.logger.error(f'Unhandled error on {request.url}')
        item = dict()
        item["Source_Page"] = 'Unknown'
        item["Link_Text"] = None
        item["Broken_Page_Link"] = request.url
        item["HTTP_Code"] = 'DNSLookupError or other unhandled'
        item["External"] = not follow_this_domain(request.url)
        yield item

    def parse_external(self, response, source, text):

        if response.status != 200:
            item = dict()

            item["Source_Page"] = source
            item["Link_Text"] = text
            item["Broken_Page_Link"] = response.url
            item["HTTP_Code"] = response.status
            item["External"] = not follow_this_domain(response.url)

            yield item


if __name__ == '__main__':
    run_spider(FindBrokenSpider)
