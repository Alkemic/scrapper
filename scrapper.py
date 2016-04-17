from __future__ import unicode_literals

import re
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

REGEXP_LINK = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE,
)


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


def select_content(selector, content, response, full_tag=False, callback=None):
    try:
        value = content.select(selector)[0]
        if not full_tag:
            value = value.string
    except IndexError:
        value = None

    if callback:
        value = callback(value, content, response)

    return value


class CrawlerField(object):
    def __init__(self, selector='', callback=None, full_tag=False):
        if not selector:
            raise ValueError('You have to specify `selector`')

        self.full_tag = full_tag
        self.selector = selector
        self.callback = callback

        self._value = None

    def __repr__(self):
        return '%s(\'%s\', %s, %s)' % (
            self.__class__.__name__,
            self.selector,
            self.callback,
            self.full_tag,
        )

    def __get__(self, instance, owner=None):
        return self._value

    def __set__(self, instance, value):
        self._value = value

    def process(self, content, response):
        self._value = select_content(
            self.selector, content, response, self.full_tag, self.callback,
        )


class CrawlerItem(object):
    def __new__(cls, *args, **kwargs):
        cls._base_fields = {}

        for attr_name, field in cls.__dict__.items():
            if isinstance(field, CrawlerField):
                cls._base_fields[attr_name] = field

        return super(CrawlerItem, cls).__new__(cls, *args, **kwargs)

    def __init__(self, url, caller=None, content=None):
        self._caller = caller
        self._url = url
        self.__dict__.update(copy.deepcopy(self._base_fields))

        if content is None:
            self._response = fetch_data(self._url)
            self._content = BeautifulSoup(self._response.content)
        else:
            self._response = None
            self._content = BeautifulSoup(content)

        for name, field in self.__dict__.items():
            if isinstance(field, CrawlerField):
                field.process(self._content, self._response)

    def __getattribute__(self, name):
        if not name.startswith('_') and name in self.__dict__:
            return self.__dict__[name].__get__(self)

        return super(CrawlerItem, self).__getattribute__(name)

    def as_dict(self):
        return {
            name: getattr(self, name)
            for name, field
            in self.__dict__.items()
            if isinstance(field, CrawlerField)
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
        if not self.next_selector and not self.links_selector:
            raise ScrapperException(
                'You should define either`links_selector` or `next_selector`'
            )

        if self.links_selector is not None and \
                not isinstance(self.links_selector, (tuple, list)):
            self.links_selector = self.links_selector,

        if self.next_selector is not None and \
                not isinstance(self.next_selector, (tuple, list)):
            self.next_selector = self.next_selector,

        if not self.item_class:
            raise ScrapperException('You need to setup `item_class`')

        if not issubclass(self.item_class, (CrawlerItem, CrawlerMultiItem)):
            raise ScrapperException(
                '`item_class` need to be instance of `CrawlerItem` or '
                '`CrawlerMultiItem`'
            )

        if not self.next_selector and not self.links_selector:
            raise ScrapperException(
                'You need to setup `next_selector` or `self.links_selector`'
            )

        self.response = fetch_data(self.url)
        self.content = self.response.content

    def __iter__(self):
        soup = BeautifulSoup(self.content)
        if self.next_selector:
            yield self.item_class(self.url, self, self.content)
            while True:
                selected_next = soup.find_all(*self.next_selector)
                if len(selected_next) == 0:
                    raise ScrapperCantFindNext(
                        'Couldn\'t find element by selector "{}"'.format(
                            self.next_selector,
                        )
                    )

                next_link = selected_next[0]
                next_url = next_link.attrs['href']
                if not REGEXP_LINK.match(next_url):
                    next_url = self.base_url + next_url

                self.content = fetch_data(next_url).content
                soup = BeautifulSoup(self.content)

                yield self.item_class(next_url, self)

        if self.links_selector:
            selected_links = soup.find_all(*self.links_selector)
            if len(selected_links) == 0:
                raise ScrapperCantFindNext(
                    'Couldn\'t find element by selector "{}"'.format(
                        self.next_selector
                    )
                )
            for link in selected_links:
                if self.base_url in link.attrs['href']:
                    link_url = link.attrs['href']
                else:
                    link_url = self.base_url + link.attrs['href']

                yield self.item_class(link_url, self)
