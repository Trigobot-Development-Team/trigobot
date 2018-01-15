import re
import json
import logging
import feedparser
import redis_conn

from calendar import timegm
from aioredis import RedisConnection
from discord import Client, Message, Channel

ANNOUNCE_CHANNEL_ID = '357975075468607491'

SHORT_HELP_TEXT = str.join('\n', [
    '$$$rss - Atualiza feeds',
    '$$$rss refresh - Atualiza feeds'
])

def help(**kwargs):
    return SHORT_HELP_TEXT

def strip_html(s: str) -> str:
    return re.sub('<[^<]+?>|\\xa0|&#34;', '', s)

def format_feed_entry(feed_name: str, entry: dict) -> str:
    # TODO: convert HTML to Markdown for readability
    # TODO: shorten link(s) (?)
    msg = '{} {} \n{}\n'.format(feed_name, entry['link'], \
                                strip_html(entry['summary']))

    # Shorten text when needed or Discord will refuse to send the message
    if len(msg) > 2000:
        msg = msg[:1994] + ' (...)'

    return msg

async def refresh_feed(client: Client, channel: Channel, redis: RedisConnection, url: str):
    logging.info('Refreshing feed %s', url)

    metadata = await redis.hgetall('feed:'+url)
    data = feedparser.parse(url)
    last_update = int(metadata['last_update'])
    new_last_update = last_update

    for entry in data['entries']:
        entry_timestamp = timegm(entry['published_parsed'])

        if metadata['last_update'] is None or \
            entry_timestamp > last_update:
            msg = format_feed_entry(metadata['name'], entry)

            await client.send_message(channel, content=msg)

            if entry_timestamp > new_last_update:
                new_last_update = entry_timestamp

    await redis.hset('feed:'+url, 'last_update', new_last_update)

async def run(client: Client, message: Message = None, **kwargs):
    redis = await redis_conn.get_connection()
    feeds = await redis.smembers('feeds')

    channel = client.get_channel(ANNOUNCE_CHANNEL_ID)

    for feed_url in feeds:
        await refresh_feed(client, channel, redis, feed_url)

    if message is not None:
        await client.send_message(message.channel, content='Feeds atualizados com sucesso')

    logging.info('RSS feeds refreshed')
