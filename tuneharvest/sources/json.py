import itertools
import requests
import objectpath
from tuneharvest.common import Link

from collections.abc import Callable, Iterable
from argparse import Namespace


def _object_path(obj: object, path: str)-> Iterable:
  yield from objectpath.Tree(obj).execute(path)


def from_json(args: Namespace)-> Iterable:
    data = requests.get(args.url).json()

    if args.objectpath:
        yield from _object_path(data, args.objectpath)

