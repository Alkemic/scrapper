#!/usr/bin/env python
from setuptools import setup


setup(
    name='Scrapper',
    version='0.1.1',
    url='https://github.com/Alkemic/scrapper',
    license='MIT',
    author='Daniel Alkemic Czuba',
    author_email='alkemic7@gmail.com',
    description='Scrapper is small, Python web scrapping library',
    py_modules=['scrapper'],
    keywords='scrapper,webscrapping',
    install_requires=[
        'beautifulsoup4==4.4.1',
        'requests == 2.5.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
