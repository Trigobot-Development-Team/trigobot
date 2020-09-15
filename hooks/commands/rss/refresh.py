import aiohttp
import async_timeout
import feedparser
import json
import logging
from pylru import lrucache
import re

import feed_state
from calendar import timegm
from discord import Client, Embed, Message, Role, TextChannel
from hashlib import md5
from management import get_role
from time import time

ANNOUNCE_CHANNEL_ID = 357975075468607491
MAX_UPDATES = 5

ICON_URL = "https://cdn.discordapp.com/icons/357975075468607490/866e9b0e471f720f592611360233f174.png?size=128"

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
    # Transform &#61 into @
    data = re.sub('&#61;', '=', data)
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
    data = re.sub('\n\s*\n', '\n\n', data)

    # Remove unknown/not needed html entities
    data = re.sub('&#\d+;', ' ', data)

    return re.sub('<[^<]+?>|\\xa0', '', data)

def format_feed_entry(role: Role, entry: dict) -> str:
    """
    Format message
    """
    author_name = re.sub('(.*@.* \(|\))', '', entry['author'])
    embed = Embed(title='**[{}]** {}'.format(role.name, strip_html(entry['title'])), \
                  color=role.color,
                  description=strip_html(entry['summary']))

    embed.add_field(name='Anúncio Original', value='[Clica aqui](' + entry['link'] + ')')
    embed.set_author(name=author_name, url=entry['link'], icon_url=ICON_URL)

    check_embed_len(embed, ' (...)')

    return embed

async def get_feed(session: aiohttp.ClientSession, url: str) -> str:
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            raw_data = await response.text()
            return feedparser.parse(raw_data)


async def refresh_feed(session: aiohttp.ClientSession, client: Client, channel: TextChannel, name: str):
    """
    Check each feed for new messages
    """
    logging.info('Refreshing feed %s', name)

    url = feed_state.get_url(name)
    last_update = feed_state.get_last_update(name)

    data = await get_feed(session, url)
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

async def publish_entry(client: Client, channel: TextChannel, name: str, entry: dict) -> None:
    """
    Send feed message and update LRU Cache
    """
    # send message
    role = get_role(client, name)
    embed = format_feed_entry(role, entry)
    msg = await channel.send(content=role.mention + '\n**' + strip_html(entry['title']) + '**', embed=embed)

    # save id & content hash to keep track of update
    published_cache[entry.link] = (msg.id, hash(embed.description))

async def check_update_entry(client: Client, channel: TextChannel, name: str, entry: dict) -> None:
    """
    Check if new version is available, replace the old message and publish a new one
    """
    try:
        (old_msg_id, old_hash) = published_cache[entry.link]

        cur_embed = format_feed_entry(get_role(client, name), entry)
        cur_hash = hash(cur_embed.description)

        if cur_hash != old_hash:
            # need to publish new version
            # repeats format_feed_entry call but it's not a perf issue
            await publish_entry(client, channel, name, entry)

            # mark old message as old
            old_msg = await channel.fetch_message(old_msg_id)
            embed = Embed(description='**ESTE ANÚNCIO FOI ATUALIZADO**\n~~' + \
                    old_msg.embeds[0].description + '~~')

            # shorten this text too
            check_embed_len(embed, ' (...)~~')

            await old_msg.edit(embed=embed)
    except KeyError:
        return

def check_embed_len(embed: Embed, padd: str = ''):
    """
    Checks if embed has correct size and padd if bigger
    """

    if len(embed) > 2048:
        embed.description = embed.description[:2048-len(padd)] + padd

async def run(client: Client, message: Message = None, **kwargs) -> None:
    """
    Run command
    """
    channel = client.get_channel(ANNOUNCE_CHANNEL_ID)

    async with aiohttp.ClientSession() as session:
        for feed_name in feed_state.get_names():
            await refresh_feed(session, client, channel, feed_name)

    if message is not None:
        await message.channel.send(content='Feeds atualizados com sucesso')

    logging.info('RSS feeds refreshed')
