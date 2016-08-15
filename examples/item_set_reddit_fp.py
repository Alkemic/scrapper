#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import scrapper


class RedditEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        '//p[@class="title"]/a/text()',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField('//p[@class="title"]/a/@href')


class RedditEntries(scrapper.CrawlerMultiItem):
    item_class = RedditEntry
    content_selector = '//*[@id="siteTable"]/div[contains(@class, "thing")]'


class RedditItemSet(scrapper.CrawlerItemSet):
    url = 'http://www.reddit.com/'
    base_url = 'http://www.reddit.com/'
    item_class = RedditEntries
    next_selector = '//a[contains(@rel, "next")]/@href'


def main():
    i = 1
    for item_set in RedditItemSet():
        for item in item_set:
            print('page: %d, title: %s (%s)' % (i, item.title, item.link))

        i += 1


if __name__ == '__main__':
    main()
