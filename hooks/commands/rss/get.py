from datetime import datetime

import aioredis
from discord import Client, Message

import redis_conn

SHORT_HELP_TEXT = '$$$rss get [name|url] - Mostra informação sobre um feeds em monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def get_url_from_name(redis: aioredis.RedisConnection, name: str) -> str:
    return await redis.get('feed:index:'+name)

def format_timestamp(timestamp: str) -> str:
    dt = datetime.utcfromtimestamp(int(timestamp))
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC%z')

async def get_feed_info(redis: aioredis.RedisConnection, url: list):
    metadata = await redis.hgetall('feed:'+url)

    return '**{}**: {}\nÚltima atualização: {}'.format(
            metadata['name'],
            url,
            format_timestamp(metadata['last_update'])
        )

async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()

    try:
        url = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: URL')

    if not url.startswith('http'):
        url = await get_url_from_name(redis, url)

    info_text = await get_feed_info(redis, url)
    await client.send_message(message.channel, content=info_text)
