import sys


def to_console(args, links):
    for link in links:
        sys.stdout.write(args.format.format(**link._asdict()))
        sys.stdout.write('\n')
