import argparse
import pkgutil
import sys


import tuneharvest.sources


from tuneharvest.sources.console import from_console
from tuneharvest.sources.discourse import from_discourse
from tuneharvest.sources.slack import from_slack
from tuneharvest.sinks.console import to_console
from tuneharvest.sinks.youtube import to_youtube
from tuneharvest.filters import Masseuse


import pkg_resources
try:
    VERSION = pkg_resources.require("tuneharvest")[0].version
except:
    VERSION = 'DEV'


DEFAULT_SOURCE = 'from console'
DEFAULT_SINK = 'to console'


def make_parser():
    parser = argparse.ArgumentParser(
        description=('Harvests youtube music links from a slack conversation' +
                     ' for posting in a youtube playlist\n' +
                     '  Version {}'
                    ).format(VERSION),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--version', action='version', version=VERSION,
        help='Print version ({}) and exit'.format(VERSION)
    )

    subparsers = parser.add_subparsers()

    from_parser = subparsers.add_parser('from', help='Read music links from a location')
    register_modules(tuneharvest.sources, from_parser.add_subparsers())

    to_parser = subparsers.add_parser('to', help='Write music links to a location')
    register_modules(tuneharvest.sinks, to_parser.add_subparsers())

    return parser


def register_modules(pkg, subparsers):
    for loader, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        mod = loader.find_module(name).load_module(name)
        register = getattr(mod, 'register', None)
        if register:
            register(subparsers)


def main(argv=None):
    parser = make_parser()
    argv = (argv or sys.argv)[1:]
    commands = list()

    prev = 1
    for i in range(prev+1, len(argv)):
        if sys.argv[i] in ('from', 'to'):
            commands.append(sys.argv[prev:i])
            prev = i
    commands.append(sys.argv[prev:])

    if not commands[-1]:
        # Might be --version or --help
        args = parser.parse_args()
        # Otherwise: truly no commands were given
        raise RuntimeError('At least one `from` or `to` command is required.')

    sources = list()
    sink = None
    for command in commands:
        if command[0] == 'from':
            sources.append(command)
        elif sink is None:
            sink = command
        else:
            raise RuntimeError('We only support one sink at a time currently')

    if not sources:
        sources.append(DEFAULT_SOURCE.split())
    if not sink:
        sink = DEFAULT_SINK.split()

    source_args = [parser.parse_args(source) for source in sources]
    sink_args = parser.parse_args(sink)

    massage = Masseuse().massage

    iter_source_links = (massage(link) for args in source_args for link in args.action(args))
    sink_args.action(sink_args, iter_source_links)

if __name__ == '__main__':
    main()

