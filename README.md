# scrapper
scrapper is small, Python web scrapping library using
[lxml](http://lxml.de/) and
[requests](http://docs.python-requests.org/en/latest/).


## Usage
First start with ``CrawlerField``, it the one that define the data you are
looking for, or more specific, it's select data from content using ``selector``
defined by you. It takes three parameters:
* ``selector`` - it's a XPath selector
* ``callback`` - (optional) a function that will be fired on data

Class ``CrawlerField`` is used to define fields inside subclass of
``CrawlerItem``:

```python
class AmazonEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        "//*[@id='productTitle']/text()",
        lambda value, content, response: value.strip() if value else None,
    )
    price = scrapper.CrawlerField(
        "//span[@class='a-color-price']/text()",
        lambda value, _, __: value.strip() if value else None,
    )
    img = scrapper.CrawlerField(
        '//div[@id="imgTagWrapperId"]/img/@data-a-dynamic-image',
        get_image,
    )
```

After creating a subclass of ``CrawlerItem`` we can instantiate it and the
constructor takes following parameters:
* ``url`` - webpage on what we are going to get data
* ``caller`` - (optional) in what class we created this instance
* ``content`` - (optional) if we already have contents of the site this is the
place to pass it

Using given example we can use it like this:
```python
product = AmazonEntry(link)
print 'title: %s\nprice: %s\nimg:%s' % (
    product.title, product.price, product.img,
)
```

### Repetitions on site
When there is more than one occurrence of data set you are looking for you, then
you should use ``CrawlerMultiItem``. It's designed to look for repetitions in
content.
When creating a class, you have to setup two attributes:
* ``content_selector`` - it's selector, that we are going to iterate over
content selected bt this
* ``item_class`` - it's a ``CrawlerItem`` subclass that look for a data in
content selected by above selector.


```python
import scrapper


class ImgurEntry(scrapper.CrawlerItem):
    link = scrapper.CrawlerField('//a[@class="image-list-link"]/@href')

    description = scrapper.CrawlerField(
        '//a[@class="hover"]/p/text()',
        lambda value, _, __: value.strip() if value else None,
    )


class ImgurEntryCollection(scrapper.CrawlerMultiItem):
    item_class = ImgurEntry
    content_selector = '//div[@class="cards"]/div[@class="post"]'


for item in ImgurEntryCollection('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
```

### Crwaling over pages on site
Class ``CrawlerItemSet`` can be used when there is need to iterate over pages.
When

* ``url`` - starting url
* ``item_class`` - class that is used for
* ``links_selector`` - XPath selector for links to pages that should be iterated
over, usually this should point to ``a`` tags in paginator
* ``next_selector`` - XPath selector for a next site


```python
import scrapper


class WykopEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        '//div[contains(@class, "lcontrast")]/h2/a/text()',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField('//div[contains(@class, "lcontrast")]/h2/a/@href')


class WykopEntries(scrapper.CrawlerMultiItem):
    item_class = WykopEntry
    content_selector = '//*[@id="itemsStream"]//li[contains(@class, "link")]'


class WykopItemSet(scrapper.CrawlerItemSet):
    url = 'http://www.wykop.pl/'
    item_class = WykopEntries
    links_selector = '//a[@class="button"]/@href'


for item_set in WykopItemSet():
    for item in item_set:
        print "title: %s (%s)" % (item.title, item.link))

```


See [/examples/](https://github.com/Alkemic/scrapper/tree/master/examples) for
more simple usages.
