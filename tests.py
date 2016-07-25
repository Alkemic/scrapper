import sys
import copy
import unittest
from mock import patch
from datetime import datetime

import requests

import scrapper


def monkey_patch_requests_get():
    def monkey_patch_get(uri, *args, **kwargs):
        extra_dict = {
            'content': open('./fixtures/%s' % uri).read(),
            'status_code': 200,
        }

        return type(
            'mocked_requests',
            (object,),
            extra_dict
        )()

    setattr(requests, 'get', monkey_patch_get)


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        monkey_patch_requests_get()


class TestCrawlerField(BaseTestCase):
    def test_raises_exception(self):
        with self.assertRaises(ValueError):
            scrapper.CrawlerField()

    def test_basic_initialisation(self):
        field = scrapper.CrawlerField('h1')

        self.assertEqual(field.selector, 'h1')
        self.assertEqual(field.full_tag, False)
        self.assertEqual(field.callback, None)
        self.assertEqual(field.value, None)
        self.assertEqual(field.__str__(), '')

    def test_returned_value_must_be_unicode(self):
        field = scrapper.CrawlerField('h1')
        field.value = 1234

        self.assertEqual(field.__str__(), '1234')
        if sys.version_info > (3, 0):
            self.assertEqual(type(field.__str__()), str)
        else:
            self.assertEqual(type(field.__str__()), unicode)

    def test_repr(self):
        field = scrapper.CrawlerField('h1')
        self.assertEqual('CrawlerField(\'h1\', None, False)', repr(field))


class TestCrawlerItem(BaseTestCase):
    def test_deepcopy(self):
        class TestCrawlerClass(scrapper.CrawlerItem):
            title = scrapper.CrawlerField('h1')

        item = TestCrawlerClass('single_entry.html')
        dup = copy.deepcopy(item)
        self.assertFalse(item is dup)
        self.assertFalse(item.title is dup.title)

    def test_unknown_selector(self):
        class TestCrawlerClass(scrapper.CrawlerItem):
            title = scrapper.CrawlerField('h12')

        item = TestCrawlerClass('single_entry.html')

        self.assertIsNone(item.title.value)

    def test_proper_initialization(self):
        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = '<html><body>' \
                                 '<h1>Test A1</h1></body></html>'

            crawler_item = scrapper.CrawlerItem('http://dummy.org')

        self.assertEqual(crawler_item._url, 'http://dummy.org')
        self.assertEqual(
            crawler_item._response,
            mocked_get,
        )
        self.assertEqual(
            str(crawler_item._content),
            '<html><body><h1>Test A1</h1></body></html>',
        )

    def test_simple_selection(self):
        class TestCrawlerClass(scrapper.CrawlerItem):
            title = scrapper.CrawlerField('h1')

        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = '<html><body>' \
                                 '<h1>Test A1</h1></body></html>'

            crawler_item = TestCrawlerClass('http://dummy.org')

        self.assertEqual(
            str(crawler_item.title),
            'Test A1',
        )

    def test_simple_content(self):
        class TestCrawlerClass(scrapper.CrawlerItem):
            title = scrapper.CrawlerField('div.wrap h1')
            author = scrapper.CrawlerField('div.wrap a')
            author_email = scrapper.CrawlerField(
                'div.wrap a',
                lambda value, content, response: value['href'].replace(
                    'emialto:', '',
                ),
                True,
            )
            content = scrapper.CrawlerField(
                'div.wrap div.content',
                lambda value, content, response: value.strip(),
            )

        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = open('./fixtures/single_entry.html').read()

            crawler_item = TestCrawlerClass('http://dummy.org')

        self.assertEqual(
            str(crawler_item.title),
            'Title',
        )
        self.assertEqual(
            str(crawler_item.author),
            'Author field',
        )
        self.assertEqual(
            str(crawler_item.author_email),
            'author@example',
        )
        self.assertEqual(
            str(crawler_item.content),
            'Lorem ipsum',
        )

        self.assertEqual(
            crawler_item.as_dict(),
            {
                'author_email': u'author@example',
                'content': u'Lorem ipsum',
                'title': u'Title',
                'author': u'Author field',
            },
        )


class TestCrawlerMultiItem(BaseTestCase):
    def test_should_throw_exception(self):
        with self.assertRaises(scrapper.ScrapperException):
            scrapper.CrawlerMultiItem(None)

        class TestClassCrawlerMultiItem(scrapper.CrawlerMultiItem):
            pass

        with self.assertRaises(scrapper.ScrapperException):
            TestClassCrawlerMultiItem(None)

        class TestClassCrawlerMultiItem(scrapper.CrawlerMultiItem):
            item_class = scrapper.CrawlerItem

        with self.assertRaises(scrapper.ScrapperException):
            TestClassCrawlerMultiItem(None)

        class TestClassCrawlerMultiItem(scrapper.CrawlerMultiItem):
            item_class = object

        with self.assertRaises(scrapper.ScrapperException):
            TestClassCrawlerMultiItem(None)

    def test_creation(self):
        class TestClassCrawlerItem(scrapper.CrawlerItem):
            name = scrapper.CrawlerField('h1')

        class TestClassCrawlerMultiItem(scrapper.CrawlerMultiItem):
            item_class = TestClassCrawlerItem
            content_selector = 'div.entry'

        multi_item = TestClassCrawlerMultiItem('page_1.html')
        items = [item for item in multi_item]
        items_names = [item.name.value for item in items]

        self.assertEqual(len(items), 4)
        self.assertEqual(items_names, [
            'Auguste Eichmann',
            'Dominick Von',
            'Scottie Skiles',
            'Almon Tromp',
        ])


class TestCrawlerItemSet(BaseTestCase):
    def test_raises_exception(self):
        with self.assertRaises(scrapper.ScrapperException):
            scrapper.CrawlerItemSet()

        class TestCrawlerItemSet(scrapper.CrawlerItemSet):
            item_class = object

        with self.assertRaises(scrapper.ScrapperException):
            TestCrawlerItemSet()

        class TestCrawlerItemSet(scrapper.CrawlerItemSet):
            item_class = scrapper.CrawlerItem

        with self.assertRaises(scrapper.ScrapperException):
            TestCrawlerItemSet()

    def test_initialisation(self):
        class TestCrawlerClass(scrapper.CrawlerItem):
            title = scrapper.CrawlerField('h1')

        class TestCrawlerItemSet(scrapper.CrawlerItemSet):
            base_url = ''
            url = 'page_index.html'
            item_class = TestCrawlerClass
            links_selector = 'a'

        item_set = TestCrawlerItemSet()
        items = [item for item in item_set]

        self.assertEqual(len(items), 3)
        items_title = [str(item.title) for item in items]

        self.assertEqual(
            items_title,
            ['Auguste Eichmann', 'Mr. Frankie Olson', 'Luke Bins'],
        )


class TestFetchDataFunction(BaseTestCase):
    def test_raises_exception(self):
        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 500
            # mocked_get.content = ''

            with self.assertRaises(scrapper.ScrapperException):
                scrapper.fetch_data('http://example.org')

    def test_delay(self):
        old_delay = scrapper.FETCH_DATA_DELAY
        scrapper.FETCH_DATA_DELAY = 1.5

        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = ''

            # first call is without delay
            scrapper.fetch_data('http://example.org')

            start = datetime.now()
            scrapper.fetch_data('http://example.org')

        delta = datetime.now() - start
        delta = delta.seconds + delta.microseconds / 1000000.0

        self.assertGreaterEqual(delta, scrapper.FETCH_DATA_DELAY)

        scrapper.FETCH_DATA_DELAY = old_delay


if __name__ == '__main__':
    unittest.main()
