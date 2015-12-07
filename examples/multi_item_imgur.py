#!/usr/bin/env python
import scrapper


def t(value, content, response):
    import ipdb;ipdb.set_trace()
    return value.strip() if value else None

class ImgurEntry(scrapper.CrawlerItem):
    # title = scrapper.CrawlerField(
    #     'h3.r > a',
    #     lambda value, content, response: value.strip() if value else None,
    # )
    link = scrapper.CrawlerField(
        'a.image-list-link',
        lambda value, content, response: value['href'] if value else None,
        True,
    )

    description = scrapper.CrawlerField(
        'a.hover > p',
        t,
        # lambda value, content, response: value.strip() if value else None,
    )


class ImgurEntryCollection(scrapper.CrawlerMultiItem):
    item_class = ImgurEntry
    content_selector = 'div.cards > div.post'


scrapper.FETCH_DATA_DELAY = 2

for item in ImgurEntryCollection('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
