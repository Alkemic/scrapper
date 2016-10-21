import re
import copy
from datetime import datetime
from time import sleep

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

import lxml.html
import lxml.etree
import requests


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


def select_content(selector, content, response, callback=None):
    value = content.xpath(selector)
    if isinstance(value, list):
        value = value[0] if len(value) else None

    if callback:
        value = callback(value, content, response)

    return value


class Field(object):
    def __init__(self, selector='', callback=None):
        if not selector:
            raise ValueError('You have to specify `selector`')

        self.selector = selector
        self.callback = callback

        self._value = None

    def __repr__(self):
        return '%s(\'%s\', %s)' % (
            self.__class__.__name__,
            self.selector,
            self.callback,
        )

    def __get__(self, instance, owner=None):
        return self._value

    def __set__(self, instance, value):
        self._value = value

    def process(self, content, response):
        self._value = select_content(
            self.selector, content, response, self.callback,
        )


class Item(object):
    def __new__(cls, *_, **__):
        cls._base_fields = {}

        for attr_name, field in cls.__dict__.items():
            if isinstance(field, Field):
                cls._base_fields[attr_name] = field

        return super(Item, cls).__new__(cls)

    def __init__(self, url, caller=None, content=None):
        self._caller = caller
        self._url = url
        self.__dict__.update(copy.deepcopy(self._base_fields))

        if content is None:
            self._response = fetch_data(self._url)
            self._content = lxml.html.fromstring(self._response.content)
        else:
            self._response = None
            self._content = lxml.html.fromstring(content)

        for _, field in self.__dict__.items():
            if isinstance(field, Field):
                field.process(self._content, self._response)

    def __getattribute__(self, name):
        if not name.startswith('_') and name in self.__dict__:
            return self.__dict__[name].__get__(self)

        return super(Item, self).__getattribute__(name)

    def as_dict(self):
        return {
            name: getattr(self, name)
            for name, field
            in self.__dict__.items()
            if isinstance(field, Field)
        }


class ItemSet(object):
    # iterates over items fetched by this selection in BS
    content_selector = None

    # should be instance of Item
    item_class = None

    def __init__(self, url, caller=None, content=None):
        self.url = url
        self.caller = caller

        if not self.item_class:
            raise ScrapperException('You need to setup `item_class`')

        if not issubclass(self.item_class, (Item, ItemSet)):
            raise ScrapperException('`item_class` need to be instance of '
                                    '`Item` or `Pagination`')

        if not self.content_selector:
            raise ScrapperException('You need to define `content_selector`')

        if content is None:
            self.response = fetch_data(self.url)
            self.content = self.response.content
        else:
            self.response = None
            self.content = content

    def __iter__(self):
        parsed = lxml.html.fromstring(self.content)
        for content in parsed.xpath(self.content_selector):
            # pylint: disable=not-callable
            yield self.item_class(self.url, self, lxml.etree.tostring(content))


class Pagination(object):
    url = None

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

        if not self.item_class:
            raise ScrapperException('You need to setup `item_class`')

        if not issubclass(self.item_class, (Item, ItemSet)):
            raise ScrapperException(
                '`item_class` need to be instance of `Item` or '
                '`Pagination`'
            )

        if not self.next_selector and not self.links_selector:
            raise ScrapperException(
                'You need to setup `next_selector` or `self.links_selector`'
            )

        self.response = fetch_data(self.url)
        self.content = self.response.content

    def next_link(self):
        parsed = lxml.html.fromstring(self.content)

        if self.next_selector:
            yield self.url
            while True:
                selected_next = parsed.xpath(self.next_selector)
                if len(selected_next) == 0:
                    raise ScrapperCantFindNext(
                        'Couldn\'t find element by selector "{}"'.format(
                            self.next_selector,
                        )
                    )

                next_url = selected_next[0]
                if not REGEXP_LINK.match(next_url):
                    next_url = urljoin(self.url, next_url)

                self.content = fetch_data(next_url).content
                parsed = lxml.html.fromstring(self.content)

                yield next_url

        if self.links_selector:
            selected_links = parsed.xpath(self.links_selector)

            if len(selected_links) == 0:
                raise ScrapperCantFindNext(
                    'Couldn\'t find element by selector "{}"'.format(
                        self.next_selector
                    )
                )

            for link in selected_links:
                yield urljoin(self.url, link)

    def __iter__(self):
        for next_link in self.next_link():
            # pylint: disable=not-callable
            yield self.item_class(next_link, self)
