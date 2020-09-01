import feedparser
from discord import Client, Message

import feed_state
from policy import AccessControl

SHORT_HELP_TEXT = '$$$rss add <name> <url> [last_update] - Adiciona feed RSS para monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'])
async def run(client: Client, message: Message, **kwargs):
    args = kwargs['args']
    if len(args) < 1:
        raise ValueError('Missing arguments: name, url')
    elif len(args) < 2:
        raise ValueError('Missing argument: url')
    elif len(kwargs['args']) > 3:
        raise ValueError('Too many arguments')

    # Test the feed
    url = args[1]
    try:
        feedparser.parse(url)
    except Exception:
        raise ValueError('Invalid feed URL: {}'.format(url))

    feed_state.add(*kwargs['args'])

    await message.channel.send(content='Feito')
