import re
import json
import logging
import feedparser
import redis_conn

from time import time
from calendar import timegm
from aioredis import RedisConnection
from discord import Client, Message, Channel
from hashlib import md5

ANNOUNCE_CHANNEL_ID = '357975075468607491'
MAX_UPDATES = 5

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

def hashtext(text: str) -> int:
    hash_object = md5(text.encode())    # generates the md5 hash of a given str
    return hash_object.hexdigest()

async def refresh_feed(client: Client, channel: Channel, redis: RedisConnection, url: str):
    logging.info('Refreshing feed %s', url)

    metadata = await redis.hgetall('feed:'+url)
    data = feedparser.parse(url)
    last_update = int(metadata['last_update'])
    new_last_update = last_update
    cur_timestamp = time()

    for entry in data['entries']:
        entry_timestamp = timegm(entry['published_parsed'])

        if metadata['last_update'] is None or \
            entry_timestamp > last_update:

            await publish_entry(client, channel, redis, metadata['name'], entry)

            if entry_timestamp > new_last_update:
                new_last_update = entry_timestamp
        else:
            if cur_timestamp - entry_timestamp < 3600*24*7: # perf: only try updating up to 3-day old entries
                await check_update_entry(client, channel, redis, metadata['name'], entry)

    await redis.hset('feed:'+url, 'last_update', new_last_update)

async def publish_entry(client: Client, channel: Channel, redis: RedisConnection, name: str, entry: dict):
    # send message
    msg_content = format_feed_entry(name, entry)
    msg = await client.send_message(channel, content=msg)

    # save id & content hash to keep track of updates
    key = 'lastupdate:'+entry.link
    tr = redis.multi_exec() # save and set expiration atomically
    tr.set(key, hashtext(msg_content) + message.id)
    tr.expire(key, 3600 * 48) # ignore updates after two days
    await tr.execute()

async def check_update_entry(client: Client, channel: Channel, redis: RedisConnection, name: str, entry: dict):
    last_published_entry = await redis.get('lastupdate:'+entry.link)
    if last_published_entry is not None:
        old_msg_id = last_published_entry[32:]
        old_hash = last_published_entry[:32]

        cur_msg_content = format_feed_entry(name, entry)
        cur_hash = hashtext(cur_msg_content)

        if cur_hash != old_hash:
            # repeats format_feed_entry call but it's not a perf issue
            publish_entry(client, channel, redis, name, entry)

            # mark old message as old
            old_msg = await client.get_message(channel, old_msg_id)
            new_content = '**ESTE ANÚNCIO FOI ATUALIZADO**\n~~' + old_msg.content + '~~'
            await client.edit_message(old_msg, new_content=new_content)

async def run(client: Client, message: Message = None, **kwargs):
    redis = await redis_conn.get_connection()
    feeds = await redis.smembers('feeds')

    channel = client.get_channel(ANNOUNCE_CHANNEL_ID)

    for feed_url in feeds:
        await refresh_feed(client, channel, redis, feed_url)

    if message is not None:
        await client.send_message(message.channel, content='Feeds atualizados com sucesso')

    logging.info('RSS feeds refreshed')
