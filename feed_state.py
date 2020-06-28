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
    with open(STATE_PATH, 'w') as f:
        json.dump(_feeds, f)

def loads(feeds: str):
    _feeds = json.loads(feeds)
    save()

def dumps():
    return json.dumps(_feeds)

def add(name: str, url: str, last_update: float = time.time()):
    if name in _feeds:
        raise ValueError('Feed already exists: `%s`' % name)

    _state[name] = { 'url': url, 'last_update': last_update }
    save()

def delete(name: str):
    if name not in _feeds:
        raise ValueError('No such feed: `%s`' % name)

    del _feeds[name]
    save()

def update(name: str, last_update: float):
    _feeds[name]['last_update'] = last_update
    save()

def get_names() -> Iterator:
    return _feeds.keys()

def get_url(name: str) -> str:
    return _feeds[name]['url']

def get_last_update(name: str) -> float:
    return _feeds[name]['last_update']
