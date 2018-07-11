import re
import json
import logging
import feedparser
import redis_conn

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

    for entry in data['entries']:
        entry_timestamp = timegm(entry['published_parsed'])

        if metadata['last_update'] is None or \
            entry_timestamp > last_update:
            msg = format_feed_entry(metadata['name'], entry)

            message = await client.send_message(channel, content=msg)

            if entry_timestamp > new_last_update:
                new_last_update = entry_timestamp

            # Add update to hash, field=url, value=hash+message_id
            field = entry.link
            value = hashtext(msg) + message.id
            await redis.hset('updates:'+url, field, value)

    await redis.hset('feed:'+url, 'last_update', new_last_update)
    await check_changes(client, channel, redis, url)
    await keep_short(client, channel, redis, url)

async def check_changes(client: Client, channel: Channel, redis: RedisConnection, url: str):
    logging.info('Checking for changes in feed %s', url)

    metadata = await redis.hgetall('feed:'+url)
    data = feedparser.parse(url)
    for entry in data['entries']:
        field = entry.link

        if await redis.hexists('updates:'+url, field):
            msg = format_feed_entry(metadata['name'], entry)
            new_hash = hashtext(msg)

            value = await redis.hget('updates:'+url, field)
            old_hash = value[:32]

            if new_hash != old_hash:
                message_id = value[32:]
                message = await client.edit_message(message_id, content = msg)
                value = new_hash + message.id
                await redis.hset('updates:'+url, field, value)

async def keep_short(client: Client, channel: Channel, redis: RedisConnection, url: str):
    # If the hash has more than MAX_UPDATES updates delete the oldest one
    hash_len = await redis.hlen('updates:'+url)
    if hash_len > MAX_UPDATES:
        hash_ = await redis.hgetall('updates':+url) # Returns the hash as a dict
        hash_fields = keys(hash_)

        field = hash_fields[0]
        value = hash_[field]
        msg_id = value[32:]
        msg = await client.get_message(channel, msg_id)
        early_time = msg.timestamp
        for f in hash_fields[1:]:

            temp_value = hash_[f]
            temp_msg_id = temp_value[32:]
            temp_msg = await client.get_message(channel, msg_id)

            if temp_msg.timestamp < early_time:
                field = temp_field
                early_time = temp_msg.timestamp

        await redis.hdel('updates:'+url, field)

async def run(client: Client, message: Message = None, **kwargs):
    redis = await redis_conn.get_connection()
    feeds = await redis.smembers('feeds')

    channel = client.get_channel(ANNOUNCE_CHANNEL_ID)

    for feed_url in feeds:
        await refresh_feed(client, channel, redis, feed_url)

    if message is not None:
        await client.send_message(message.channel, content='Feeds atualizados com sucesso')

    logging.info('RSS feeds refreshed')
