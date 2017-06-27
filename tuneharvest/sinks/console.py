import sys

from collections.abc import Callable, Iterable
from argparse import Namespace


def register(subparsers):
    to_console_parser = subparsers.add_parser('console', help='Write links found to stdout')
    to_console_parser.set_defaults(action=to_console)

    to_console_parser.add_argument(
        '--format', '-F', default='{media}',
        help='Format to write to console'
    )
    to_console_parser.add_argument(
        '--limit', '-L', default=None, type=int,
        help='Max items to print'
    )


def to_console(args: Namespace, links: Iterable, write: Callable = None):
    write = write or sys.stdout.write
    format = (args.format + '\n').format
    limit = args.limit or -1

    for i, link in enumerate(links):
        write(format(**link._asdict()))
        if i + 1 >= limit > 0:
            return
