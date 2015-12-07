#!/usr/bin/env python
import scrapper


class SearchEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        'h3.r > a',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField(
        'h3.r > a',
        lambda value, content, response: value['href'] if value else None,
        True,
    )


class SearchEntryCollection(scrapper.CrawlerMultiItem):
    item_class = SearchEntry
    content_selector = 'div.srg > div.g'


class SearchPageItemSet(scrapper.CrawlerItemSet):
    url = 'https://www.google.pl/search?q=python'
    base_url = 'http://www.reddit.com/'
    item_class = SearchEntryCollection
    # next_selector = ('a', {'rel': 'next'})
    next_selector = 'a', {'class': 'pn'}


scrapper.FETCH_DATA_DELAY = 2

i = 1
for item_set in SearchPageItemSet():
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))

    i += 1
