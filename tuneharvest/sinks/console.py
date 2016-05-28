import sys

from collections.abc import Callable, Iterable
from argparse import Namespace


def to_console(args: Namespace, links: Iterable, write: Callable = None):
    write = write or sys.stdout.write
    format = (args.format + '\n').format
    limit = args.limit or -1

    for i, link in enumerate(links):
        write(format(**link._asdict()))
        if i + 1 >= limit > 0:
            return
