#!/usr/bin/env python
from __future__ import unicode_literals

import json

import scrapper


def get_image(value, content, response):
    try:
        mapping = json.loads(value['data-a-dynamic-image'])
        mapping = {d[0] * d[1]: url for url, d in mapping.items()}
        return mapping[max(mapping.keys())]
    except (KeyError, ValueError, TypeError):
        return None


class AmazonEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        '#productTitle',
        lambda value, content, response: value.strip(),
    )
    price = scrapper.CrawlerField(
        'div.feature span.a-color-price',
        lambda value, content, response: value.strip(),
    )
    img = scrapper.CrawlerField(
        '#imgTagWrapperId img.a-dynamic-image',
        get_image,
        True,
    )


links = [
    'http://www.amazon.co.uk/Lenovo-ThinkPad-T430s-i5-3320M-N1RLQGE/dp/'
    'B00AQPBA8U/ref=sr_1_1?ie=UTF8&qid=1449485817&sr=8-1&keywords=t430s',
    'http://www.amazon.co.uk/Lenovo-ThinkPad-T430s-23539WU-Notebook/dp/'
    'B009UESY2I/ref=pd_sim_sbs_147_4?ie=UTF8&dpID=41ZwThpTAOL&dpSrc=sims'
    '&preST=_AC_UL160_SR160%2C160_&refRID=1MQ4F7Y27EX36HCAPMP8',
    'http://www.amazon.co.uk/Lenovo-Thinkpad-14-inch-i5-2520M-Professional'
    '/dp/B004WNAYS4/',
]

products = [AmazonEntry(link) for link in links]
for product in products:
    print('title: {}\nprice: {}\nimg: {}'.format(
        product.title, product.price, product.img,
    ))
