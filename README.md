# NPOGO
It's not Ai. It's NPOGO.

![NPOGO](data/splash.jpeg?raw=true "NPOGO")

NPOGO is a high-speed web-crawler designed to scrape partner contact and organiational information from non-profit websites. It allows for the scheduling of recurring crawls and handles errors, network timeouts, and anti-bot software automatically. 

Please crawl responsibley.

### Getting Started
To execute the program  
``scrapy runspider main.py``  

To scrape contact information for partners  
``scrapy runspider info_crawl.py`` - ensure generated partner.json is in same directory  
``scrapy runspider -a filename=IN_FILE -a outfile=OUT_FILE info_crawl.py`` - optional .txt file of urls can be passed in

##### Dependancies:
```python
scrapy
pyap
``` 

This program attempts to find all possible partner non-profit organizations given a set of "seed URLs".
These URLs will serve as input for the program.

The program will attempt to traverse all possible links on a page that match our criteria.

Finally, all partners will be parsed in an attempt to find contact information using the 
``info_crawl.py`` spider.

Output is currently in JSON format, with hopes to expose an API that will return neighbors for a 
set of URLs.  

**Current state**: Scraper will list all links that follow a valid "partner path" as partners. 
Work still needs to be done on scraping non ``<a>`` style partners, i.e. ``<ul>`` or 
``<div>`` items. These partners are stored in a "low_confidence" entry as initial results 
have been poor. 

```json
{
    "www.ccrcda.org": {
        "breadcrumbs": [
            "http://www.ccrcda.org/agencies_and_programs/",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-Tri-County-Services_109_13_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Saratoga-Warren-Washington-Counties_109_2_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-of-Columbia-and-Greene-Counties_109_3_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-of-Herkimer-County_109_4_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-of-Delaware-Otsego-Schoharie_109_5_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-of-Fulton-Montgomery-Counties_109_6_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Care-Coordination-Services_110_7_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-Disabilities-Services_110_8_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Senior-Caregiver-Support-Services_110_9_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Community-Maternity-Services_110_10_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Catholic-Charities-Housing-Office_110_11_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/United-Tenants-of-Albany_110_12_sb.htm",
            "http://www.ccrcda.org/agencies_and_programs/Additional-Programs_111_pg.htm",
            "http://www.ccrcda.org/agencies_and_programs/2016-Migrant-Crisis_125_pg.htm"
        ],
        "partners": [
            "https://www.spiraldesign.com/",
            "http://www.cchoalbany.org",
            "http://www.depaulhousing.com",
            "https://www.ccseniorservices.org/",
            "http://www.ccherkimercounty.org/",
            "https://www.catholiccharitiescg.org"
        ]
    }
}
```

All output and a history will be kept in the local directory under ``debug/``.

**Notes:** 

- You may want to adjust the ``DOWNLOAD_TIMEOUT`` setting in ``main.py``. It is currently set to
5 seconds (default is 180) for quicker debugging.
- There may be some problems executing in the Windows environment, namely in the ``os`` functions.
- **Python 3.6 is required.**

You can prepend ``--`` to any line in the seed file to exclude it from being read in.

``main.py`` - crawling logic  
``info_crawl.py`` - crawling logic for partner site contact information
``utils.py`` - data cleaning and utilities  
``partner_kw.txt`` - keywords to grab partner data  
``stop_kw.txt`` - stop words  
``partner_urls.txt`` - seed URLs  
``slim_urls.txt`` - test/debug URLs  
``output.json`` - JSON object representation relations between partners and base sites  
``partner.json`` - JSON representation of all found partners and their corresponding contact information  
``log.txt`` - scrapy log. also include s traces of URLs and which keywords/stop words were used to traverse.
