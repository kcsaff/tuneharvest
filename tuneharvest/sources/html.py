import itertools
import requests
from bs4 import BeautifulSoup
from tuneharvest.common import Link

from collections.abc import Callable, Iterable
from argparse import Namespace


def _lazyyt(soup: BeautifulSoup)-> Iterable:
  for item in soup.find_all('div', ['lazyYT'], {'data-youtube-id': True}):
        yield Link(service='youtube', itemid=item['data-youtube-id'])


def from_html(args: Namespace)-> Iterable:
    data = requests.get(args.url).text

    soup = BeautifulSoup(data, 'html.parser')

    if args.lazyyt:
      yield from _lazyyt(soup)

