import argparse
import sys

from tuneharvest.sources.console import from_console
from tuneharvest.sources.slack import from_slack
from tuneharvest.sinks.console import to_console
from tuneharvest.sinks.youtube import to_youtube
from tuneharvest.filters import Masseuse


parser = argparse.ArgumentParser(
    'tuneharvest',
    description='Can harvest youtube music links from a slack conversation for posting in a youtube playlist.'
)

subparsers = parser.add_subparsers()

from_parser = subparsers.add_parser('from', help='Read music links from a location')
from_subparsers = from_parser.add_subparsers()

from_console_parser = from_subparsers.add_parser('console', help='Read links line by line from stdin')
from_console_parser.set_defaults(action=from_console)

from_console_parser.add_argument(
    '--format', '-F', default='{media}',
    help='Format to read from console'
)


from_slack_parser = from_subparsers.add_parser('slack', help='Read links based on a slack search')
from_slack_parser.set_defaults(action=from_slack)

from_slack_parser.add_argument(
    '--token', '-t', default='token-from-slack.txt',
    help='Slack API token or filename containing API token'
)
from_slack_parser.add_argument(
    '--query', '-q', default='has:link',
    help='Slack search query'
)
from_slack_parser.add_argument(
    '--direction', '-D', default='desc', choices=('asc', 'desc'),
    help='Slack sort direction'
)
from_slack_parser.add_argument(
    '--limit', '-L', default=None, type=int,
    help='Max number of items to find'
)


to_parser = subparsers.add_parser('to', help='Write music links to a location')
to_subparsers = to_parser.add_subparsers()

to_console_parser = to_subparsers.add_parser('console', help='Write links found to stdout')
to_console_parser.set_defaults(action=to_console)

to_console_parser.add_argument(
    '--format', '-F', default='{media}',
    help='Format to write to console'
)


to_youtube_parser = to_subparsers.add_parser('youtube', help='Update a youtube playlist')
to_youtube_parser.set_defaults(action=to_youtube)

to_youtube_parser.add_argument(
    '--secrets', '-S', default='secrets-to-youtube.json',
    help='JSON client secrets file'
)
to_youtube_parser.add_argument(
    '--title', '-T', default=None,
    help='Title of youtube playlist'
)
to_youtube_parser.add_argument(
    '--id', '-I', default=None,
    help='Youtube playlist ID to modify'
)
to_youtube_parser.add_argument(
    '--privacy', default='unlisted', choices=('private', 'public', 'unlisted'),
    help='Privacy setting of new youtube playlist'
)
to_youtube_parser.add_argument(
    '--limit', '-L', default=200, type=int,
    help='Max number of items in playlist'
)
to_youtube_parser.add_argument(
    '--reverse', default=False, type=bool,
    help='Whether to reverse link order'
)
to_youtube_parser.add_argument(
    '-v', '--verbose', action='count', default=0,
    help='Verbosity'
)


def main(argv=None):
    argv = (argv or sys.argv)[1:]
    commands = list()

    prev = 1
    for i in range(prev+1, len(argv)):
        if sys.argv[i] in ('from', 'to'):
            commands.append(sys.argv[prev:i])
            prev = i
    commands.append(sys.argv[prev:])

    if not commands[-1]:
        parser.parse_args()
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
        sources.append('from console'.split())
    if not sink:
        sink = 'to console'.split()

    source_args = [parser.parse_args(source) for source in sources]
    sink_args = parser.parse_args(sink)

    massage = Masseuse().massage

    iter_source_links = (massage(link) for args in source_args for link in args.action(args))
    sink_args.action(sink_args, iter_source_links)

if __name__ == '__main__':
    main()
