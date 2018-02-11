from aioredis import RedisConnection
from discord import Client, Message

from .get import get_url_from_name

import redis_conn
from policy import AccessControl

SHORT_HELP_TEXT = '$$$rss remove [name|url] - Remove feed do sistema'

def help(**kwargs):
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'])
async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()

    try:
        url = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: URL')

    if not url.startswith('http'):
        url = await get_url_from_name(redis, url)

    name = await redis.hget('feed:'+url, 'name')

    pipe = redis.pipeline()
    pipe.srem('feeds', url)
    pipe.delete('feed:'+url)
    pipe.delete('feed:index:'+name)

    await pipe.execute()
    await client.send_message(message.channel, content='Feito')
