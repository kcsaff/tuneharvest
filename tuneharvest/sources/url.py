import itertools
import requests
from bs4 import BeautifulSoup
from tuneharvest.common import Link

from collections.abc import Callable, Iterable
from argparse import Namespace


def _lazyyt(soup: BeautifulSoup)-> Iterable:
    for item in soup.find_all('.lazyYT', {'data-youtube-id': True}):
        yield Link(service='youtube', itemid=item['data-youtube-id'])


def from_url(args: Namespace)-> Iterable:
    data = requests.get(args.url).text

    soup = BeautifulSoup(data)

    if args.lazyyt:
      yield from _lazyyt(soup)

