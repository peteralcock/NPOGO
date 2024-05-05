from scrapy import signals
import scrapy
import utils
import json
import pyap
import re

partner_file = 'partner.json'

class OrgInfoCrawler(scrapy.Spider):
    name = 'infocrawler'

    def __init__(self, filename='partner_urls.txt', outfile=None, **kwargs):
        # default to loading partner_file if .json is found
        ext = str(filename).split('.')[-1]
        self.outfile = outfile
        # load in urls from plain text file
        if ext != 'json':
            self.data = {}
            self.urls = utils.get_urls(filename)
        # load in generated output from main.py
        else:
            with open(partner_file, 'r') as f:
                self.data = json.load(f)
            self.urls = [k for k in self.data.keys()]
        super().__init__(**kwargs)

    # some sites were taking forever
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 5,
        'LOG_FILE': 'info_crawl_log.txt'
    }

    # register closing event
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(OrgInfoCrawler, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    # start requests
    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=utils.clean_url(url), callback=self.parse_url, meta={'key': url})

    # TODO: need to 'go deeper' to look for addresses and phone numbers
    # parsing only homepages right now
    def parse_url(self, response):
        # get all text on page as plain text
        text = ''.join(response.xpath('//body//text()').extract())
        key = response.meta.get('key')

        # url might not be here if usr is passing in plain file
        if key not in self.data:
            self.data[key] = {
                'url': key,
                'name': [],
                'phone': [],
                'address': []
            }

        # parse out address
        for addr in pyap.parse(text, country='US'):
            self.data[key]['address'].append(addr.as_dict())

        # https://stackoverflow.com/questions/34527917/extracting-phone-numbers-from-a-free-form-text-in-python-by-using-regex
        for phone in re.finditer(r'\(?\b[2-9][0-9]{2}\)?[-. ]?[2-9][0-9]{2}[-. ]?[0-9]{4}\b', text):
            print(phone)
            self.data[key]['phone'].append(phone.group())

    # write out new data
    def spider_closed(self):
        print('closing')
        with open(f'{self.outfile}', 'w') as f:
            f.write(json.dumps(self.data, indent=4))