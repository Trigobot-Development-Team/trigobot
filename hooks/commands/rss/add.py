import feedparser
from aioredis import RedisConnection
from discord import Client, Message

import redis_conn
from policy import AccessControl
from .setdate import get_current_timestamp

SHORT_HELP_TEXT = '$$$rss add [name] [url] - Adiciona feed RSS para monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def add_feed(redis: RedisConnection, name: str, url: str):
    if await redis.sismember('feeds', url):
        raise ValueError('Feed already being tracked: {}'.format(url))

    current_timestamp = get_current_timestamp()

    # Send all commands together for efficiency
    pipe = redis.pipeline()
    pipe.hset('feed:'+url, 'name', name)
    pipe.hset('feed:'+url, 'last_update', current_timestamp)
    pipe.set('feed:index:'+name, url)
    pipe.sadd('feeds', url)

    await pipe.execute()

@AccessControl(roles=['Staff'])
async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()

    try:
        name = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: name')

    try:
        url = kwargs['args'][1]
    except IndexError:
        raise ValueError('Missing argument: url')

    # Test the feed
    try:
        feedparser.parse(url)
    except Exception:
        raise ValueError('Invalid feed URL: {}'.format(url))

    await add_feed(redis, name, url)

    await client.send_message(message.channel, content='Feito')
