#!/usr/bin/env python
from __future__ import print_function

import scrapper


class ImgurEntry(scrapper.Item):
    link = scrapper.Field('.//a[@class="image-list-link"]/@href')

    description = scrapper.Field('.//div[@class="hover"]/p/text()')


class ImgurItemSet(scrapper.ItemSet):
    item_class = ImgurEntry
    content_selector = '//div[@class="cards"]/div[@class="post"]'


for item in ImgurItemSet('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
