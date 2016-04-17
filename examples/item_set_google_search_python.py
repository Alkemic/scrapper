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
    base_url = 'https://www.google.pl/'
    item_class = SearchEntryCollection
    next_selector = 'a', {'id': 'pnnext'}


i = 1
items_set = SearchPageItemSet()
for item_set in items_set:
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))

    i += 1
