# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


class CrawlerField(object):
    selector = None
    value = ''

    def __init__(self, selector='', callback=None):
        if not selector:
            raise ValueError('You have to specify `selector`')

        self.selector = selector
        self.callback = callback

    def __str__(self):
        return self.value


class CrawlerItem(object):
    def __init__(self, url):
        self._response = requests.get(url)
        self._content = BeautifulSoup(self._response.content)

        for attr_name in dir(self):
            field = getattr(self, attr_name)
            if isinstance(field, CrawlerField):
                try:
                    value = self._content.select(field.selector)[0].string
                except IndexError:
                    value = None

                if field.callback:
                    value = field.callback(value, self._response)

                field.value = value


class CrawlerFactory(object):
    url = ''
    base_url = ''
    links_selector = ''

    content = None

    item_class = CrawlerItem

    def __init__(self):
        self.content = requests.get(self.url).content

    def __iter__(self):
        soup = BeautifulSoup(self.content)
        for link in soup.select(self.links_selector):
            yield self.item_class(self.base_url + link.attrs['href'])
