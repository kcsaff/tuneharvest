from collections import namedtuple
import httplib2
import sys
import itertools
import json
import os
from warnings import warn

from collections.abc import Callable, Iterable
from argparse import Namespace

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from tuneharvest.common import Link
from tuneharvest.utils import unique, make_lists_equal


PLAYLIST_ITEMS_MAX = 50


PlaylistItem = namedtuple('PlaylistItem', ('itemid', 'deleteid'))


def _ignore(*_):
    pass


debug = _ignore


def _client(secrets: str):
    flow = flow_from_clientsecrets(
        secrets,
        message='Missing secrets!', scope='https://www.googleapis.com/auth/youtube'
    )
    keys_dirname = os.path.dirname(os.path.abspath(secrets))
    storage_filename = os.path.join((keys_dirname, '{}-oauth2.json'.format(sys.argv[0])))
    storage = Storage(storage_filename)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args(args=[])
        credentials = run_flow(flow, storage, flags)

    youtube = build(
        'youtube', 'v3',
        http=credentials.authorize(httplib2.Http())
    )
    return youtube


def create_playlist(youtube, title: str, description: str, privacy: str = 'unlisted')-> str:
    playlists_insert_response = youtube.playlists().insert(
        part='snippet,status',
        body=dict(
            snippet=dict(
                title=title,
                description=description
            ),
            status=dict(
                privacyStatus=privacy
            )
        )
    ).execute()
    return playlists_insert_response['id']


def get_or_create_playlist(youtube, title: str, description: str, privacy: str = 'unlisted')-> str:
    desired_title = title.lower().strip()
    for playlist in youtube.playlists().list(
        part='snippet',
        mine=True,
    ).execute()['items']:
        this_title = playlist['snippet']['title'].lower().strip()
        if this_title == desired_title:
            return playlist['id']
    else:
        return create_playlist(youtube, title, description, privacy=privacy)


def iter_playlist_items(youtube, playlist_id: str)-> Iterable:
    request = youtube.playlistItems().list(
        playlistId=playlist_id,
        part='snippet',
        maxResults=PLAYLIST_ITEMS_MAX,
    )
    while request:
        response = request.execute()
        for video in response['items']:
            debug(video)
            video_id = video['snippet']['resourceId']['videoId']
            delete_id = video['id']
            yield PlaylistItem(video_id, delete_id)
        request = youtube.playlistItems().list_next(request, response)


_FAILURE = object()

_ACCEPTABLE_FAILURES = {
    (403, 'playlistItemsNotAccessible'),
    (404, 'videoNotFound'),
}


def update_playlist(youtube, playlist_id: str, links: Iterable):
    old_items = list(iter_playlist_items(youtube, playlist_id))
    new_items = list(links)

    def are_equal(new_item: Link, old_item: PlaylistItem)-> bool:
        return new_item.itemid == old_item.itemid

    # Making callbacks that will be used in a call to ``make_lists_equal``
    def handle_http_errors(fun: Callable):
        def do_it(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except HttpError as err:
                status = int(err.args[0]['status'])
                try:
                    data = json.loads(err.args[1].decode())
                except:
                    warn('Could not interpret body {}'.format(err.args[1]))
                    raise err
                else:
                    debug(data)
                    reasons = {(status, d['reason']) for d in data['error']['errors']}
                    if reasons & _ACCEPTABLE_FAILURES:
                        return _FAILURE
                    debug(err)
                    debug(err.args)
                raise
        return do_it

    @handle_http_errors
    def do_insert(position: int, new_item: Link):
        debug('Inserting at {}: {}'.format(position, new_item))
        youtube.playlistItems().insert(
            part='snippet,contentDetails',
            body=dict(
                snippet=dict(
                    playlistId=playlist_id,
                    resourceId=dict(
                        kind='youtube#video',
                        videoId=new_item.itemid,
                    ),
                    position=position,
                ),
                contentDetails=dict(
                    note=new_item.context,
                )
            )
        ).execute()

    @handle_http_errors
    def do_append(new_item: Link):
        debug('Appending: {}'.format(new_item))
        youtube.playlistItems().insert(
            part='snippet,contentDetails',
            body=dict(
                snippet=dict(
                    playlistId=playlist_id,
                    resourceId=dict(
                        kind='youtube#video',
                        videoId=new_item.itemid,
                    ),
                ),
                contentDetails=dict(
                    note=new_item.context,
                )
            )
        ).execute()

    @handle_http_errors
    def do_delete(position, old_item: PlaylistItem):
        debug('Deleting from {}: {}'.format(position, old_item))
        youtube.playlistItems().delete(
            id=old_item.deleteid,
        ).execute()

    make_lists_equal(
        new_items, old_items,
        equals=are_equal,
        insert=do_insert, append=do_append, delete=do_delete,
        failure=_FAILURE,
    )


def to_youtube(args: Namespace, links: Iterable):
    global debug
    debug = print if args.verbose >= 2 else _ignore

    youtube = _client(args.secrets)

    if args.id:
        playlist_id = args.id
    elif args.title:
        playlist_id = get_or_create_playlist(
            youtube, args.title, 'Tuneharvested playlist {}'.format(args.title), args.privacy
        )
    else:
        raise RuntimeError('Require either playlist ID or title')

    # Filter links to just those desired, using iterator ops
    debug('Ready to filter youtube')
    links = (link for link in links if link.service == 'youtube' and link.itemid)
    debug('Ready to get unique items')
    links = unique(links, lambda link: link.itemid)
    if args.limit > 0:
        debug('Ready to get limited items ({})'.format(args.limit))
        links = itertools.islice(links, 0, args.limit)
    links = list(links)

    if args.reverse:
        links.reverse()

    debug('Ready to update playlist')
    update_playlist(youtube, playlist_id, links)


