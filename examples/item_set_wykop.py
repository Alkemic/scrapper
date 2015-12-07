#!/usr/bin/env python
import scrapper


class WykopEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        'div.lcontrast > h2 > a',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField(
        'div.lcontrast > h2 > a',
        lambda value, content, response: value['href'] if value else None,
        True,
    )


class WykopEntries(scrapper.CrawlerMultiItem):
    item_class = WykopEntry
    content_selector = '#itemsStream > li.link'


class WykopItemSet(scrapper.CrawlerItemSet):
    url = 'http://www.wykop.pl/'
    base_url = 'http://www.wykop.pl/'
    item_class = WykopEntries
    links_selector = 'a', {'class': 'button'},


scrapper.FETCH_DATA_DELAY = .4

i = 1
for item_set in WykopItemSet():
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))

    i += 1
