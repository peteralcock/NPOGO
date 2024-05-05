from urllib.parse import urlsplit

# gets a list of the urls to crawl initially
# -- are prepended to links to ignore
def get_urls(filename='partner_urls.txt') -> list:
    urls = []
    for url in _read_file(filename):
        if url.startswith('--'):
            print(f'Ignoring {url}')
            continue
        urls.append(clean_url(url))
    return urls

# adds protocol to links
def clean_url(url):
    if not url.startswith('http'):
        return f'http://{url}'
    return url

# gets a list of the partner keywords
def get_kws(filename='partner_kw.txt'):
    return _read_file(filename)

# reads in filename as read only, returns list of stripped strings from file
def _read_file(filename):
    with open(filename, 'r') as file:
        return [kw.strip() for kw in file.readlines()]

# check to see if any of the partner words are in URL
def partner_match(url, logger=None):
    if not url:
        return False

    # the elegant solution is this
    if not logger:
        return any(kw in url for kw in get_kws())

    # but for logging purposes we will be verbose
    kws = get_kws()
    for kw in kws:
        if kw in url:
            logger.info(f'✅ {kw} was found in {url}.')
            return True

# check to see if any of the stop words are in URL
def stop_word_match(url, logger=None):
    if not url:
        return False

    # the elegant solution is this
    if not logger:
        return any(kw in url for kw in get_kws('stop_kw.txt'))

    # but for logging purposes we will be verbose
    kws = get_kws('stop_kw.txt')
    for kw in kws:
        if kw in url:
            logger.info(f'🛑 {kw} was encountered in {url}.')
            return True

# check to see if URL is on path of detecting partner
def valid_partner_url(url, logger=None):
    return partner_match(url, logger) and not stop_word_match(url, logger)

# extracts the hostname of a given website
# i.e. stackoverflow.com/questions/12345 -> www.stackoverflow.com
def get_hostname(url):
    hostname = urlsplit(url).hostname

    # already in good form
    if not hostname:
        return url

    if not hostname.startswith('www'):
        return f'www.{hostname}'
    return hostname

# validates a URL to see if it is a potential partner link
def valid_partner(base, url, logger=None):
    return (get_hostname(base) != get_hostname(url) and
            not stop_word_match(url, logger) and
            'tel' not in url and
            'jpg' not in url)