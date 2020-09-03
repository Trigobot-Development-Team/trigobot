import feedparser
import json
import logging
from pylru import lrucache
import re

import feed_state
from calendar import timegm
from discord import Client, Message, Role, TextChannel
from hashlib import md5
from management import get_role
from time import time

ANNOUNCE_CHANNEL_ID = 750401922267086948
MAX_UPDATES = 5

SHORT_HELP_TEXT = str.join('\n', [
    '$$$rss - Atualiza feeds',
    '$$$rss refresh - Atualiza feeds'
])

# non-persistent state: message IDs for updating feed entries
# maps entry.link -> (message_id, content_hash)
published_cache = lrucache(128)

def help(**kwargs) -> str:
    """
    Show help
    """
    return SHORT_HELP_TEXT

def strip_html(data: str) -> str:
    """
    Convert HTML to Markdown
    """
    # Transform &amp; into &
    data = re.sub('&amp;', '&', data)
    # Transform &lt; into <
    data = re.sub('&lt;', '<', data)
    # Transform &#34; into "
    data = re.sub('&#34;', '"', data)
    # Transform &#39; into '
    data = re.sub('&#39;', '\'', data)
    # Transform &#64 into @
    data = re.sub('&#64;', '@', data)
    # Transform <br> into newline
    data = re.sub('<br[^><\w]*\/?>', '\n', data)
    # Transform <i> into italic
    data = re.sub('<\/?i[^<>\w]*>', '*', data)
    # Transform <b> into bold
    data = re.sub('<\/?b[^<>\w]*>', '**', data)
    # Transform headings in newlines and spaces
    data = re.sub('<h\d?[^<>\w]*>', ' ', data)
    data = re.sub('<\/h\d?[^<>\w]*>', '\n', data)
    # Transform some divs into spaces
    data = re.sub('</div[^<>\w]*>[^\w\n]*<div[^<>\w]*>', '\n', data)
    # Avoid multiple whitespace
    data = re.sub('\n{3,}', '\n', data)
    data = re.sub('\s{3,}', ' ', data)

    return re.sub('<[^<]+?>|\\xa0', '', data)

def format_feed_entry(role: Role, entry: dict) -> str:
    """
    Format message
    """
    # TODO: shorten link(s) (?)
    msg = '**{}** {}\n{}'.format(role.mention, entry['link'], \
                                strip_html(entry['summary']))

    # Shorten text when needed or Discord will refuse to send the message
    if len(msg) > 2000:
        msg = msg[:1994] + ' (...)'

    return msg

def hashtext(text: str) -> int:
    """
    Generate MD5 digest
    """
    hash_object = md5(text.encode())    # generates the md5 hash of a given str
    return hash_object.hexdigest()

async def refresh_feed(client: Client, channel: TextChannel, name: str):
    """
    Check each feed for new messages
    """
    logging.info('Refreshing feed %s', name)

    url = feed_state.get_url(name)
    last_update = feed_state.get_last_update(name)

    data = feedparser.parse(url)
    new_last_update = last_update
    cur_timestamp = time()

    for entry in data['entries']:
        entry_timestamp = timegm(entry['published_parsed'])

        if last_update is None or entry_timestamp > last_update:
            await publish_entry(client, channel, name, entry)

            if entry_timestamp > new_last_update:
                new_last_update = entry_timestamp
        else:
            await check_update_entry(client, channel, name, entry)

    feed_state.update(name, new_last_update)

async def publish_entry(client: Client, channel: TextChannel, name: str, entry: dict):
    """
    Send feed message and update LRU Cache
    """
    # send message
    msg_content = format_feed_entry(get_role(client, name), entry)
    msg = await channel.send(content=msg_content)

    # save id & content hash to keep track of updates
    published_cache[entry.link] = (msg.id, hashtext(msg_content))

async def check_update_entry(client: Client, channel: TextChannel, name: str, entry: dict):
    """
    Check if new version is available, replace the old message and publish a new one
    """
    try:
        (old_msg_id, old_hash) = published_cache[entry.link]

        cur_msg_content = format_feed_entry(get_role(client, name), entry)
        cur_hash = hashtext(cur_msg_content)

        if cur_hash != old_hash:
            # need to publish new version
            # repeats format_feed_entry call but it's not a perf issue
            await publish_entry(client, channel, name, entry)

            # mark old message as old
            old_msg = await channel.fetch_message(old_msg_id)
            warn_content = '**ESTE ANÚNCIO FOI ATUALIZADO**\n~~' + \
                    old_msg.content + '~~'

            # shorten this text too
            if len(warn_content) > 2000:
               warn_content = warn_content[:1992] + ' (...)~~'
            await old_msg.edit(content=warn_content)
    except KeyError:
        return

async def run(client: Client, message: Message = None, **kwargs):
    """
    Run command
    """
    channel = client.get_channel(ANNOUNCE_CHANNEL_ID)

    for feed_name in feed_state.get_names():
        await refresh_feed(client, channel, feed_name)

    if message is not None:
        await message.channel.send(content='Feeds atualizados com sucesso')

    logging.info('RSS feeds refreshed')
