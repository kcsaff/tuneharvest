import sys
from tuneharvest.common import Link
from parse import parse


def from_console(args):
    for line in sys.readlines():
        line = line.strip()
        if line:
            parsed = parse(line)
            yield Link(*parsed.fixed, **parsed.named)
