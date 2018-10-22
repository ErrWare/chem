import msl
import re
import logging
import time
import json
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.debug('starting')
wikins = 'https://en.wikipedia.org'

wikiptpage = msl.getSoup('https://en.wikipedia.org/wiki/Periodic_table')

tables = wikiptpage.find_all('table', style=True)
table = list(t for t in tables if '!important' in t.attrs['style'])[2]

hrefs = list(a.attrs['href'] for a in table.find_all('a', href=True) if a.attrs['href'].startswith('/wiki/'))
elementlinks = list(href for href in hrefs if 'block' not in href)
logger.debug(elementlinks)
logger.debug('Found {} elements as above'.format(len(elementlinks)))
periodic_table = defaultdict(dict)
for e in elementlinks:
    try:
        esoup = msl.getSoup(wikins+e)
        infobox = esoup.find('table', class_='infobox')
        name = re.search('([A-Z][a-z]*)$', infobox.caption.text).group()
        # find atomic weight
        aw_marker = infobox.find('a',string=['Standard atomic weight', 'Mass number'])
        td = aw_marker.parent.parent.td
        for junk in td.find_all('span',style='display:none'):
            junk.decompose()
        aw_text = td.text
        if 'conventional' in aw_text:
            aw_text[aw_text.index('conv'):]
        mo = re.search(r'([1-9]\d*\.\d+|\d{2,3})',aw_text)
        masses = mo.groups()
        mass = max(masses,key=lambda m:len(m))
        logger.debug('{} has mass {}'.format(name,mass))
        periodic_table[name]['mass'] = float(mass)
    except AttributeError as e:
        logging.exception('Could not find {}\'s mass in <{}>'.format(name, aw_text))
        time.sleep(6)
        continue

with open('periodic_table.json', 'w') as file:
    json.dump(periodic_table, file)