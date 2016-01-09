# scrapper
scrapper is small, Python web scrapping library using 
[BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/) and 
[requests](http://docs.python-requests.org/en/latest/).


## Usage
First start with ``CrawlerField``, it the one that define the data you are
looking for, or more specific, it's select data from content using ``selector``
defined by you. It takes three parameters:
* ``selector`` - it's a XPath selector
* ``callback`` - (optional) a function that will be fire on data
* ``full_tag`` - (optional) tells if we want data with tag, i.e. 
``<a href="http://example/">link</a>`` instead of ``link``

Class ``CrawlerField`` is used to define fields inside subclass of 
``CrawlerItem``:

```python
class AmazonEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField('#productTitle')
    price = scrapper.CrawlerField(
        'div.feature span.a-color-price',
        lambda value, content, response: value.strip(),
    )
    img = scrapper.CrawlerField(
        '#imgTagWrapperId img.a-dynamic-image',
        get_image,
        True,
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
    link = scrapper.CrawlerField(
        'a.image-list-link',
        lambda value, _, __: value['href'] if value else None,
        True,
    )

    description = scrapper.CrawlerField(
        'a.hover > p',
        lambda value, _, __: value.strip() if value else None,
    )


class ImgurEntryCollection(scrapper.CrawlerMultiItem):
    item_class = ImgurEntry
    content_selector = 'div.cards > div.post'


for item in ImgurEntryCollection('http://imgur.com/'):
    print("url: %s; %s" % (item.link, item.description))
```

### Crwaling over pages on site
Class ``CrawlerItemSet`` can be used when there is need to iterate over pages.
When

* ``url`` - starting url
* ``base_url`` - base url for links that are relative
* ``item_class`` - class that is used for 
* ``links_selector`` - selector for links to pages that should be iterated over,
usually this should point to ``a`` tags in paginator
* ``next_selector`` - selector for a next site, XPath, can be string or tuple 
consists of string and dict, that are used to select 


```python
import scrapper

class WykopEntry(scrapper.CrawlerItem):
    title = scrapper.CrawlerField(
        'div.lcontrast > h2 > a',
        lambda value, content, response: value.strip() if value else None,
    )
    link = scrapper.CrawlerField(
        'div.lcontrast > h2 > a',
        lambda value, content, response: value['href'] if value else None,
        True,
    )


class WykopEntries(scrapper.CrawlerMultiItem):
    item_class = WykopEntry
    content_selector = '#itemsStream > li.link'


class WykopItemSet(scrapper.CrawlerItemSet):
    url = 'http://www.wykop.pl/'
    base_url = 'http://www.wykop.pl/'
    item_class = WykopEntries
    links_selector = 'a', {'class': 'button'},


for item_set in WykopItemSet():
    for item in item_set:
        print "title: %s (%s)" % (item.title, item.link))

```


See [/examples/](https://github.com/Alkemic/scrapper/tree/master/examples) for 
simple usages.


## TODO
* Make it Python 3.x compatible
