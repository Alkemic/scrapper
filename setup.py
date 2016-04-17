#!/usr/bin/env python
from setuptools import setup


setup(
    name='Scrapper',
    version='0.1.0',
    url='https://github.com/Alkemic/scrapper',
    license='MIT',
    author='Daniel Alkemic Czuba',
    author_email='alkemic7@gmail.com',
    description='Scrapper is small, Python web scrapping library',
    py_modules=['scrapper'],
    keywords='scrapper,webscrapping',
    install_requires=[
        'beautifulsoup4==4.3.2',
        'requests == 2.5.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
