import json
import os
import time

from collections.abc import Iterator


STATE_PATH = os.environ.get('TRIGOBOT_RSS_FEED_STATE', './feed_state.json')

_feeds = dict()

try:
    with open(STATE_PATH, 'r') as f:
        _feeds = json.load(f)
except FileNotFoundError:
    pass

def save():
    global _feeds
    with open(STATE_PATH, 'w') as f:
        json.dump(_feeds, f)

def loads(feeds: str):
    global _feeds
    _feeds = json.loads(feeds)
    save()

def dumps() -> str:
    global _feeds
    return json.dumps(_feeds)

def add(name: str, url: str, last_update: float = 0):
    global _feeds
    if name in _feeds:
        raise ValueError('Feed already exists: `%s`' % name)

    _feeds[name] = { 'url': url, 'last_update': last_update }
    save()

def delete(name: str):
    global _feeds
    if name not in _feeds:
        raise ValueError('No such feed: `%s`' % name)

    del _feeds[name]
    save()

def update(name: str, last_update: float):
    global _feeds
    _feeds[name]['last_update'] = last_update
    save()

def get_names() -> Iterator:
    global _feeds
    return _feeds.keys()

def get_url(name: str) -> str:
    global _feeds
    return _feeds[name]['url']

def get_last_update(name: str) -> float:
    global _feeds
    return _feeds[name]['last_update']
