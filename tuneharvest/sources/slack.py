import itertools
from tuneharvest.common import Link
from slacker import Slacker


def _lookup(result, path, default=None):
    for part in path.split('.'):
        if part in result:
            result = result[part]
        else:
            return default
    return result


def _paging(contents, paging, method, *args, **kwargs):
    for page in itertools.count(kwargs.get('page', 1)):
        kwargs.update(page=page)
        body = method(*args, **kwargs).body
        for item in _lookup(body, contents):
            yield item
        page_info = _lookup(body, paging)
        if page_info['page'] >= page_info['pages']:
            break


def from_slack(args):
    token = open(args.token, 'r').read().strip()
    slack = Slacker(token)

    query = args.query
    if 'has:link' not in query.split():
        query += ' has:link'

    found = 0
    for message in _paging(
        'messages.matches',
        'messages.paging',
        slack.search.messages, query, sort='timestamp', sort_dir=args.direction
    ):
        context = message['permalink']
        for attachment in message.get('attachments', ()):
            service = attachment.get('service_name', '').lower() or None
            media = attachment.get('title_link')
            if media:
                yield Link(media, context, service, None)
                found += 1
                if args.limit is not None and found >= args.limit > 0:
                    return
