#!/usr/bin/env python
import scrapper


class WykopEntry(scrapper.Item):
    title = scrapper.Field(
        '//div[contains(@class, "lcontrast")]/h2/a/text()',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.Field('//div[contains(@class, "lcontrast")]/h2/a/@href')


class WykopEntries(scrapper.Pagination):
    item_class = WykopEntry
    content_selector = '//*[@id="itemsStream"]//li[contains(@class, "link")]'


class WykopItemSet(scrapper.ItemSet):
    url = 'http://www.wykop.pl/'
    base_url = 'http://www.wykop.pl/'
    item_class = WykopEntries
    links_selector = '//a[@class="button"]/@href'


i = 1
for item_set in WykopItemSet():
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))

    i += 1

