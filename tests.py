import copy
import unittest
from mock import patch
from datetime import datetime

import lxml.etree
import requests

import scrapper


def monkey_patch_requests_get():
    def monkey_patch_get(uri, *args, **kwargs):
        with open('./fixtures/%s' % uri) as fh:
            extra_dict = {
                'content': fh.read(),
                'status_code': 200,
            }

        return type(
            str('mocked_requests'),
            (object,),
            extra_dict,
        )()

    setattr(requests, 'get', monkey_patch_get)


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        monkey_patch_requests_get()


class TestField(BaseTestCase):
    def test_raises_exception(self):
        with self.assertRaises(ValueError):
            scrapper.Field()

    def test_basic_initialisation(self):
        field = scrapper.Field('h1')

        self.assertEqual(field.selector, 'h1')
        self.assertEqual(field.callback, None)
        self.assertEqual(field._value, None)
        self.assertEqual(field.__get__(None), None)

    def test_returned_value_must_be_exact(self):
        field = scrapper.Field('//h1/text()')
        field._value = 1234

        self.assertEqual(str(field.__get__(None)), '1234')
        self.assertEqual(type(field.__get__(None)), int)

    def test_repr(self):
        field = scrapper.Field('//h1/text()')
        self.assertEqual('Field(\'//h1/text()\', None)', repr(field))


class TestItem(BaseTestCase):
    def test_deepcopy(self):
        class TestCrawlerClass(scrapper.Item):
            title = scrapper.Field('//h1/text()')

        item = TestCrawlerClass('single_entry.html')
        dup = copy.deepcopy(item)
        self.assertFalse(item is dup)
        self.assertFalse(item.title is dup.title)

    def test_unknown_selector(self):
        class TestCrawlerClass(scrapper.Item):
            title = scrapper.Field('//h12/text()')

        item = TestCrawlerClass('single_entry.html')

        self.assertIsNone(item.title)

    def test_proper_initialization(self):
        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = '<html><body>' \
                                 '<h1>Test A1</h1></body></html>'

            crawler_item = scrapper.Item('http://dummy.org')

        self.assertEqual(crawler_item._url, 'http://dummy.org')
        self.assertEqual(
            crawler_item._response,
            mocked_get,
        )
        self.assertEqual(
            lxml.etree.tostring(crawler_item._content).decode(),
            '<html><body><h1>Test A1</h1></body></html>',
        )

    def test_simple_selection(self):
        class TestCrawlerClass(scrapper.Item):
            title = scrapper.Field('//h1/text()')

        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            mocked_get.content = '<html><body>' \
                                 '<h1>Test A1</h1></body></html>'

            crawler_item = TestCrawlerClass('http://dummy.org')

        self.assertEqual(
            crawler_item.title,
            'Test A1',
        )

    def test_simple_content(self):
        class TestCrawlerClass(scrapper.Item):
            title = scrapper.Field('//div[@class="wrap"]/h1/text()')
            author = scrapper.Field('//div[@class="wrap"]/a/text()')
            author_email = scrapper.Field(
                '//div[@class="wrap"]/a/@href',
                lambda value, content, response: value.replace(
                    'emialto:', '',
                ),
            )
            content = scrapper.Field(
                '//div[@class="wrap"]/div[@class="content"]/text()',
                lambda value, content, response: value.strip(),
            )

        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 200
            with open('./fixtures/single_entry.html') as fh:
                mocked_get.content = fh.read()

            crawler_item = TestCrawlerClass('http://dummy.org')

        self.assertEqual(
            crawler_item.title, 'Title',
        )
        self.assertEqual(
            crawler_item.author, 'Author field',
        )
        self.assertEqual(
            crawler_item.author_email, 'author@example',
        )
        self.assertEqual(
            crawler_item.content, 'Lorem ipsum',
        )

        self.assertEqual(
            crawler_item.as_dict(),
            {
                'author_email': 'author@example',
                'content': 'Lorem ipsum',
                'title': 'Title',
                'author': 'Author field',
            },
        )


class TestPagination(BaseTestCase):
    def test_should_throw_exception(self):
        with self.assertRaises(scrapper.ScrapperException):
            scrapper.Pagination()

        class TestClassPagination(scrapper.Pagination):
            pass

        with self.assertRaises(scrapper.ScrapperException):
            TestClassPagination()

        class TestClassPagination(scrapper.Pagination):
            item_class = scrapper.Item

        with self.assertRaises(scrapper.ScrapperException):
            TestClassPagination()

        class TestClassPagination(scrapper.Pagination):
            item_class = object

        with self.assertRaises(scrapper.ScrapperException):
            TestClassPagination()

    def test_creation(self):
        class TestClassItem(scrapper.Item):
            name = scrapper.Field('//h1/text()')

        class TestClassPagination(scrapper.Pagination):
            item_class = TestClassItem
            content_selector = '//div[@class="entry"]'

        multi_item = TestClassPagination('page_1.html')
        items = [item for item in multi_item]
        items_names = [item.name for item in items]

        self.assertEqual(len(items), 4)
        self.assertEqual(items_names, [
            'Auguste Eichmann',
            'Dominick Von',
            'Scottie Skiles',
            'Almon Tromp',
        ])


class TestPagination(BaseTestCase):
    def test_raises_exception(self):
        with self.assertRaises(scrapper.ScrapperException):
            scrapper.Pagination()

        class TestItemSet(scrapper.Pagination):
            item_class = object

        with self.assertRaises(scrapper.ScrapperException):
            TestItemSet()

        class TestPagination(scrapper.Pagination):
            item_class = scrapper.Item

        with self.assertRaises(scrapper.ScrapperException):
            TestPagination()

    def test_initialisation(self):
        class TestCrawlerClass(scrapper.Item):
            title = scrapper.Field('//h1/text()')

        class TestPagination(scrapper.Pagination):
            base_url = ''
            url = 'page_index.html'
            item_class = TestCrawlerClass
            links_selector = '//a/@href'

        item_set = TestPagination()
        items = [item for item in item_set]

        self.assertEqual(len(items), 3)
        items_title = [item.title for item in items]

        self.assertEqual(
            items_title,
            ['Auguste Eichmann', 'Mr. Frankie Olson', 'Luke Bins'],
        )


class TestFetchDataFunction(BaseTestCase):
    def test_raises_exception(self):
        with patch('requests.get') as mock:
            mocked_get = mock.return_value
            mocked_get.status_code = 500

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
