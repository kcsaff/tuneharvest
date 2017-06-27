import sys
from tuneharvest.common import Link
from parse import parse

from collections.abc import Iterable
from argparse import Namespace


def register(subparsers):
    from_console_parser = subparsers.add_parser('console', help='Read links line by line from stdin')
    from_console_parser.set_defaults(action=from_console)

    from_console_parser.add_argument(
        '--format', '-F', default='{media}',
        help='Format to read from console'
    )


def from_console(args: Namespace)-> Iterable:
    for line in sys.readlines():
        line = line.strip()
        if line:
            parsed = parse(line)
            yield Link(*parsed.fixed, **parsed.named)
