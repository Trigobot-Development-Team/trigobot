
import json

from discord import Client, Message

import redis_conn

SHORT_HELP_TEXT = '$$$rss dump - Devolve backup da informação dos feeds (JSON)'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()
    feed_urls = await redis.smembers('feeds')

    dump = []
    for url in feed_urls:
        data = await redis.hgetall('feed:' + url)
        data['url'] = url

        dump.append(data)

    await message.channel.send(content=json.dumps(dump))
