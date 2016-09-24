#!/usr/bin/env python
import scrapper


class SearchEntry(scrapper.Item):
    title = scrapper.Field(
        '//h3[@class="r"]/a/text()',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.Field('//h3[@class="r"]/a/@href')


class SearchEntryCollection(scrapper.ItemSet):
    item_class = SearchEntry
    content_selector = '//div[@class="srg"]/div[@class="g"]'


class SearchPageItemSet(scrapper.Pagination):
    url = 'https://www.google.pl/search?q=python'
    base_url = 'https://www.google.pl/'
    item_class = SearchEntryCollection
    next_selector = '//a[@id="pnnext"]/@href'


i = 1
items_set = SearchPageItemSet()
for item_set in items_set:
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))
    if i > 10:
        break
    i += 1
