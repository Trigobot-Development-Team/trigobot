import json
import os
import time
import asyncio

from collections.abc import Iterator

from management import check_role_channel

STATE_PATH = os.environ.get('TRIGOBOT_RSS_FEED_STATE', './feed_state.json')

_feeds = dict()

def save() -> None:
    """
    Persist feed data
    """
    global _feeds
    with open(STATE_PATH, 'w') as f:
        json.dump(_feeds, f)

async def loads(feeds: str) -> None:
    """
    Replace current feeds with given argument (in JSON)
    """
    global _feeds
    _feeds = json.loads(feeds)

    for feed in _feeds:
       await check_role_channel(feed)

    save()

def dumps() -> str:
    """
    Dump feeds
    """
    global _feeds
    return json.dumps(_feeds)

async def add(name: str, url: str, last_update: float = 0) -> None:
    """
    Add feed
    """
    global _feeds
    if name in _feeds:
        raise ValueError('Feed already exists: `%s`' % name)

    _feeds[name] = { 'url': url, 'last_update': last_update }
    await check_role_channel(name)
    save()

async def join(feeds: str) -> None:
    """
    Join current with given feeds
    """
    global _feeds

    feeds = json.loads(feeds)

    subtract = [x for x in feeds.keys() if x not in _feeds.keys()]
    _feeds = { **_feeds, **feeds}
    for feed in subtract:
        await check_role_channel(feed)

    save()

def delete(name: str) -> None:
    """
    Remove feed
    """
    global _feeds
    if name not in _feeds:
        raise ValueError('No such feed: `%s`' % name)

    del _feeds[name]
    save()

def update(name: str, last_update: float) -> None:
    """
    Set feed last update
    """
    global _feeds
    _feeds[name]['last_update'] = last_update
    save()

def get_names() -> Iterator:
    """
    Get the names of the feeds
    """
    global _feeds
    return _feeds.keys()

def get_url(name: str) -> str:
    """
    Get feed URL
    """
    global _feeds
    return _feeds[name]['url']

def get_last_update(name: str) -> float:
    """
    Get feed last update
    """
    global _feeds
    return _feeds[name]['last_update']

async def init() -> None:
    """
    Initialize feeds
    """
    try:
        with open(STATE_PATH, 'r') as f:
            await loads(f.read())
    except FileNotFoundError:
        pass
