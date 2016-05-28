import sys
from tuneharvest.common import Link
from parse import parse

from collections.abc import Iterable
from argparse import Namespace


def from_console(args: Namespace)-> Iterable:
    for line in sys.readlines():
        line = line.strip()
        if line:
            parsed = parse(line)
            yield Link(*parsed.fixed, **parsed.named)
