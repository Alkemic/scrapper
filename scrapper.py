from __future__ import unicode_literals

import copy
from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'

HEADERS = {
    'User-Agent': USER_AGENT,
}

FETCH_DATA_DELAY = 0.1


class ScrapperException(Exception):
    pass


class ScrapperCantFindNext(ScrapperException):
    pass


def fetch_data(url):
    if not hasattr(fetch_data, 'last_run'):
        setattr(fetch_data, 'last_run', None)

    if fetch_data.last_run is not None:
        delta = datetime.now() - fetch_data.last_run
        delta = delta.seconds + delta.microseconds/1000000.0
        if delta < FETCH_DATA_DELAY:
            sleep_for = max(0, FETCH_DATA_DELAY - delta)
            sleep(sleep_for)

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise ScrapperException(
            'Request failed, status code: %d' % response.status_code
        )

    fetch_data.last_run = datetime.now()

    return response


class CrawlerField(object):
    def __init__(self, selector='', callback=None, full_tag=False):
        if not selector:
            raise ValueError('You have to specify `selector`')

        self.full_tag = full_tag
        self.selector = selector
        self.callback = callback

        self.value = None

    def __str__(self):
        if not self.value:
            return ''

        return "%s" % self.value

    def __repr__(self):
        return '%s(\'%s\', %s, %s)' % (
            self.__class__.__name__,
            self.selector,
            self.callback,
            self.full_tag,
        )

    def process(self, content, response):
        try:
            value = content.select(self.selector)[0]
            if not self.full_tag:
                value = value.string
        except IndexError:
            value = None

        if self.callback:
            value = self.callback(value, content, response)

        self.value = value


class CrawlerItem(object):
    def __new__(cls, *args, **kwargs):
        cls._base_fields = {}

        for attr_name in dir(cls):
            field = getattr(cls, attr_name)
            if isinstance(field, CrawlerField):
                cls._base_fields[attr_name] = field

        return super(CrawlerItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, url, caller=None, content=None):
        self._caller = caller
        self._url = url
        self._fields = copy.deepcopy(self._base_fields)

        if content is None:
            self._response = fetch_data(self._url)
            self._content = BeautifulSoup(self._response.content)
        else:
            self._response = None
            self._content = BeautifulSoup(content)

        for name, field in self._fields.items():
            field.process(self._content, self._response)

    def __getattribute__(self, name):
        if not name.startswith('_') and name in self._fields:
            return self._fields[name]

        return super(CrawlerItem, self).__getattribute__(name)

    def as_dict(self):
        return {
            name: field.value
            for name, field
            in self._fields.items()
        }


class CrawlerMultiItem(object):
    # iterates over items fetched by this selection in BS
    content_selector = None

    # should be instance of CrawlerItem
    item_class = None

    def __init__(self, url, caller=None, content=None):
        self.url = url
        self.caller = caller

        if not self.item_class:
            raise ScrapperException('You need to setup `item_class`')

        if not issubclass(self.item_class, (CrawlerItem, CrawlerMultiItem)):
            raise ScrapperException('`item_class` need to be instance of '
                                    '`CrawlerItem` or `CrawlerMultiItem`')

        if not self.content_selector:
            raise ScrapperException('You need to define `content_selector`')

        if content is None:
            self.response = fetch_data(self.url)
            self.content = self.response.content
        else:
            self.response = None
            self.content = content

    def __iter__(self):
        soup = BeautifulSoup(self.content)
        for content in soup.select(self.content_selector):
            yield self.item_class(self.url, self, str(content))


class CrawlerItemSet(object):
    url = None
    base_url = None

    # iterates over this selection, to get items
    # string - css selector for select() method or tuple - css selector and
    # other params for find_all() method
    links_selector = None

    # next link selector to next url to process
    next_selector = None

    item_class = None

    def __init__(self):
        if not self.item_class:
            raise ScrapperException('You need to setup `item_class`')

        if not issubclass(self.item_class, (CrawlerItem, CrawlerMultiItem)):
            raise ScrapperException('`item_class` need to be instance of '
                                    '`CrawlerItem` or `CrawlerMultiItem`')

        if not self.next_selector and not self.links_selector:
            raise ScrapperException('You need to setup `next_selector` '
                                    'or `self.links_selector`')

        self.response = fetch_data(self.url)
        self.content = self.response.content

    def __iter__(self):
        soup = BeautifulSoup(self.content)

        if self.next_selector:
            while True:
                if isinstance(self.next_selector, tuple):
                    selected_next = soup.find_all(*self.next_selector)
                else:
                    selected_next = soup.find_all(self.next_selector)

                if len(selected_next) == 0:
                    raise ScrapperCantFindNext(
                        'Couldn\'t find element by selector "{}"'.format(
                            self.next_selector
                        )
                    )

                next_link = selected_next[0]

                if self.base_url in next_link.attrs['href']:
                    next_url = next_link.attrs['href']
                else:
                    next_url = self.base_url + next_link.attrs['href']

                yield self.item_class(next_url, self, self.content)

                soup = BeautifulSoup(self.content)
                self.content = fetch_data(next_url).content

        for link in soup.select(self.links_selector):
            if self.base_url in link.attrs['href']:
                link_url = link.attrs['href']
            else:
                link_url = self.base_url + link.attrs['href']

            yield self.item_class(link_url, self)
