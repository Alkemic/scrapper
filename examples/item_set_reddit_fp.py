#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import scrapper


class RedditEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        'p.title > a',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField(
        'p.title > a',
        lambda value, content, response: value['href'] if value else None,
        True,
    )


class RedditEntries(scrapper.CrawlerMultiItem):
    item_class = RedditEntry
    content_selector = '#siteTable > div.thing'


class RedditItemSet(scrapper.CrawlerItemSet):
    url = 'http://www.reddit.com/'
    base_url = 'http://www.reddit.com/'
    item_class = RedditEntries
    next_selector = ('a', {'rel': 'next'})


scrapper.FETCH_DATA_DELAY = .4


def main():
    i = 1
    for item_set in RedditItemSet():
        for item in item_set:
            print('page: %d, title: %s (%s)' % (i, item.title, item.link))

        i += 1


if __name__ == '__main__':
    main()
