import itertools
import re
import requests
from tuneharvest.common import Link

from collections.abc import Callable, Iterable
from argparse import Namespace


TOPIC_RE = re.compile(r'.+/t/[^\./]+')


def _topic_path(path: str, num: int =0):
    return '{}/{}.json'.format(TOPIC_RE.match(path).group(0), num)


def _posts(path: str):
    last_post = -1
    posts_seen = 1
    while posts_seen > 0:
        posts_seen = 0
        data = requests.get(_topic_path(path, last_post + 1)).json()
        for post in data['post_stream']['posts']:
            if post['post_number'] > last_post:
                posts_seen += 1
                last_post = post['post_number']
                yield post


def _link_urls(path: str):
    for post in _posts(path):
        for link in post.get('link_counts', ()):
            yield link['url']


def from_discourse(args: Namespace)-> Iterable:
    for url in _link_urls(args.url):
        yield Link(media=url)

