import asyncio
from functools import partial

from discord import Client, Message

import redis_conn
from .get import get_feed_info

SHORT_HELP_TEXT = '$$$rss list - Lista feeds em monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()
    feed_urls = await redis.smembers('feeds')

    message_text = ''
    for url in feed_urls:
        message_text += await get_feed_info(redis, url) + '\n'

    if not message_text:
        message_text = 'Lista vazia'

    await message.channel.send(content=message_text)
