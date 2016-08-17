#!/usr/bin/env python
from __future__ import print_function

import scrapper


class ImgurEntry(scrapper.CrawlerItem):
    link = scrapper.CrawlerField('.//a[@class="image-list-link"]/@href')

    description = scrapper.CrawlerField('.//div[@class="hover"]/p/text()')


class ImgurEntryCollection(scrapper.CrawlerMultiItem):
    item_class = ImgurEntry
    content_selector = '//div[@class="cards"]/div[@class="post"]'


for item in ImgurEntryCollection('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
