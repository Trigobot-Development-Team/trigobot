from datetime import datetime

from discord import Client, Message

import feed_state

SHORT_HELP_TEXT = '$$$rss get <name> - Mostra informação sobre um feeds em monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

def format_timestamp(timestamp: float) -> str:
    dt = datetime.utcfromtimestamp(timestamp)
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC%z')

def format_feed(name: str) -> str:
    url = feed_state.get_url(name)
    last_update = feed_state.get_last_update(name)

    return '**{}**: {}\nÚltima atualização: {}'.format(
            name,
            url,
            format_timestamp(last_update)
        )

async def run(client: Client, message: Message, **kwargs):
    try:
        url = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: name')

    await message.channel.send(content=format_feed(name))
