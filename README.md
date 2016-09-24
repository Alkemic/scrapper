# scrapper
scrapper is small, Python web scrapping library using
[lxml](http://lxml.de/) and
[requests](http://docs.python-requests.org/en/latest/).


## Usage
First start with ``Field``, it the one that define the data you are
looking for, or more specific, it's select data from content using ``selector``
defined by you. It takes three parameters:
* ``selector`` - it's a XPath selector
* ``callback`` - (optional) a function that will be fired on data

Class ``Field`` is used to define fields inside subclass of
``Item``:

```python
class AmazonEntry(scrapper.Item):
    title = scrapper.Field(
        "//*[@id='productTitle']/text()",
        lambda value, content, response: value.strip() if value else None,
    )
    price = scrapper.Field(
        "//span[@class='a-color-price']/text()",
        lambda value, _, __: value.strip() if value else None,
    )
    img = scrapper.Field(
        '//div[@id="imgTagWrapperId"]/img/@data-a-dynamic-image',
        get_image,
    )
```

After creating a subclass of ``Item`` we can instantiate it and the
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
you should use ``ItemSet``. It's designed to look for repetitions in
content.
When creating a class, you have to setup two attributes:
* ``content_selector`` - it's selector, that we are going to iterate over
content selected bt this
* ``item_class`` - it's a ``Item`` subclass that look for a data in
content selected by above selector.


```python
import scrapper


class ImgurEntry(scrapper.Item):
    link = scrapper.Field('//a[@class="image-list-link"]/@href')

    description = scrapper.Field(
        '//a[@class="hover"]/p/text()',
        lambda value, _, __: value.strip() if value else None,
    )


class ImgurEntryItemSet(scrapper.ItemSet):
    item_class = ImgurEntry
    content_selector = '//div[@class="cards"]/div[@class="post"]'


for item in ImgurEntryItemSet('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
```

### Crwaling over pages on site
Class ``Pagination`` can be used when there is need to iterate over pages.
When

* ``url`` - starting url, on this page we will search for url addresses to
process by scrapper
* ``item_class`` - class that is used for actual processing of site, need to be
instance of ``Item`` or ``Pagination``
* ``links_selector`` - XPath selector for links to pages that should be iterated
over, usually this should point to ``a`` tags in paginator
* ``next_selector`` - XPath selector for selecting next site, will always select
link from currently processed page


```python
import scrapper


class WykopEntry(scrapper.Item):
    title = scrapper.Field(
        '//div[contains(@class, "lcontrast")]/h2/a/text()',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.Field(
        '//div[contains(@class, "lcontrast")]/h2/a/@href',
    )


class WykopEntries(scrapper.ItemSet):
    item_class = WykopEntry
    content_selector = '//*[@id="itemsStream"]//li[contains(@class, "link")]'


class WykopPagination(scrapper.Pagination):
    url = 'http://www.wykop.pl/'
    item_class = WykopEntries
    links_selector = '//a[@class="button"]/@href'


for item_set in WykopPagination():
    for item in item_set:
        print "title: %s (%s)" % (item.title, item.link))

```

#### Controlling iteration

By default scrapper will go over pages selected by ``links_selector`` or select
next link on currently processed page using

Iteration over pages is done in ``next_link`` method. To manually control what
pages should be processed you need to override this method. This method must
yield single url, which is next page to crawl over.


## Examples

See [/examples/](https://github.com/Alkemic/scrapper/tree/master/examples) for
more simple usages.
