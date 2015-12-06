#!/usr/bin/env python
import scrapper


class RedditFontPageEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        'p.title > a',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField(
        'p.title > a',
        lambda value, content, response: value['href'] if value else None,
        True,
    )


class RedditFrontPageEntries(scrapper.CrawlerMultiItem):
    item_class = RedditFontPageEntry
    content_selector = '#siteTable > div.thing'


class RedditFrontPageCollection(scrapper.CrawlerItemSet):
    url = 'http://www.reddit.com/'
    base_url = 'http://www.reddit.com/'
    item_class = RedditFrontPageEntries
    next_selector = ('a', {'rel': 'next'})


scrapper.FETCH_DATA_DELAY = 2

i = 1
for item_set in RedditFrontPageCollection():
    for item in item_set:
        print("page: %d, title: %s (%s)" % (i, item.title, item.link))

    i += 1
