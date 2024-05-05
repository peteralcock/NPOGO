from scrapy import signals
import datetime
import scrapy
import utils
import json
import time
import os

timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%-m-%-d %H-%M-%S')
# change this to move debug output
debug_path = os.path.join('debug', timestamp)

os.makedirs(debug_path, exist_ok=True)

out_file = os.path.join(debug_path, 'output.json')          # JSON mapping of seed site to partners
partner_file = os.path.join(debug_path, 'partner.json')     # JSON mapping of partners to contact information
log_file = os.path.join(debug_path, 'log.txt')              # debug: scrapy log
generated_urls = os.path.join(debug_path, 'urls.txt')       # debug: actual list of parsed URLs fed to scrapy

data = {}               # contains mapping of seed site to partners
partner_info = {}       # contains mapping of partners to contact and other information

start = time.time()


# debug purposes, simple health checks
def _health_check():
    with open(generated_urls, 'r') as urls, open(out_file, 'r') as output:
        out_data = json.load(output)

        no_urls = len(urls.readlines())
        no_keys = len(out_data.keys())

        # checks to see if number of base urls matches in read urls
        if no_urls == no_keys:
            print(f'✅ URL count validation pass: read: {no_urls} stored: {no_keys}')
        else:
            print(f'🚫 Health check fail. Number of URLs read in [{no_urls}] is not the same as output [{no_keys}].')

        # checks to make sure we have an entry for every partner in partner_info
        partners = set()
        partner_pass = True
        for entry in out_data.values():
            partners.update(entry['partners'])
        for partner in partners:
            if partner not in partner_info:
                print(f'🚫 Health check fail. No contact entry for {partner}.')
                partner_pass = False
        if partner_pass:
            print(f'✅ Health check Pass. All partners have contact entry.')

        for partner_contact in partner_info:
            if partner_contact not in partners:
                print(f'⚠️ Warning: {partner_contact} in contacts but not a partner.')


class OrgCrawler(scrapy.Spider):
    def __init__(self, filename='partner_urls.txt', **kwargs):
        self.filename = filename
        super().__init__(**kwargs)

    name = 'orgcrawler'

    custom_settings = {
        #'DOWNLOAD_TIMEOUT': 5
        'LOG_FILE': log_file
    }

    # called when the spider is closed, will be used for reporting purposes
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(OrgCrawler, cls).from_crawler(crawler, *args, **kwargs)

        # register closed method
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    # get urls, generate request objects to crawl
    # will call parse() to crawl
    def start_requests(self):
        urls = utils.get_urls(filename=self.filename)

        # debug purposes
        with open(generated_urls, 'w') as f:
            for url in urls:
                f.write(f'{url}\n')

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_url)

    # crawling logic
    def parse_url(self, response):
        base = utils.get_hostname(response.url)

        # may want to add stop words for domains for bad redirects
        if 'dnsrsearch' in base:
            return
        if base not in data:
            data[base] = {
                'breadcrumbs': [],
                'partners': [],
                'low_confidence': []
            }

        # TODO: Create utils functions for the validation
        # TODO: Make selection more dynamic
        # check to see if current page has potential partners in plain text
        on_page_kws = ['members']
        if utils.valid_partner_url(response.url, self.logger):
            for header in response.xpath('//h1/text()'):
                if any(kw in header.get().lower() for kw in on_page_kws):
                    data[base]['low_confidence'] += [item.get() for item in response.xpath('//ul//li/text()')]

        # TODO: create xpath string generator this should really be
        # TODO: '//a[not(contains(@href, "youtube")) and not(contains(@href, "facebook"))]'
        # TODO: because the facebook, twitter, etc links are still being crawled just not visited
        # anything on page that matches <a> tags
        for link in response.xpath('//a'):
            # get the link name, get the link url
            link_url = link.xpath('@href').get()
            full_url = response.urljoin(link_url)

            # on the right path - keep going
            if (utils.valid_partner_url(link_url, self.logger) and                      # partner kw is in URL
                    full_url not in data[base]['breadcrumbs'] and                       # haven't already been here
                    utils.get_hostname(response.url) == utils.get_hostname(full_url)):  # still on same site

                data[base]['breadcrumbs'].append(full_url)
                yield scrapy.Request(full_url, callback=self.parse_url)

            # not a partner match, but came from  a partner page i.e mysite/partners -> yoursite.org
            elif utils.valid_partner_url(response.url):
                # get base name of partner
                partner_name = utils.get_hostname(full_url)

                # if the partner link is not in the list and make sure host names are not the same
                if partner_name not in data[base]['partners'] and utils.valid_partner(base, full_url, self.logger):
                    data[base]['partners'].append(partner_name)

                    # add template of partner info for secondary crawler
                    partner_info[partner_name] = {
                        'url': partner_name,
                        'name': [],
                        'phone': [],
                        'address': []
                    }

    # called when spider is closed
    def spider_closed(self):
        with open(out_file, 'w') as o, open(partner_file, 'w') as p:
            o.write(json.dumps(data, indent=4))
            p.write(json.dumps(partner_info, indent=4))

        _health_check()

        self.logger.info(f'Total time elapsed: {datetime.timedelta(seconds=time.time() - start)}')
        print(f'Total time elapsed: {datetime.timedelta(seconds=time.time() - start)}')