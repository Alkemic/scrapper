#!/usr/bin/env python
from __future__ import print_function

import scrapper


class ImgurEntry(scrapper.CrawlerItem):
    link = scrapper.CrawlerField(
        'a.image-list-link',
        lambda value, _, __: value['href'] if value else None,
        True,
    )

    description = scrapper.CrawlerField(
        'a.hover > p',
        lambda value, _, __: value.strip() if value else None,
    )


class ImgurEntryCollection(scrapper.CrawlerMultiItem):
    item_class = ImgurEntry
    content_selector = 'div.cards > div.post'


for item in ImgurEntryCollection('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
