from discord import Client, Message

import feed_state
from .get import format_feed

SHORT_HELP_TEXT = '$$$rss list - Lista feeds em monitorização'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    message_text = ''
    for name in feed_state.get_names():
        message_text += format_feed(name) + '\n'

    if len(message_text) == 0:
        message_text = 'Não há feeds.'

    await message.channel.send(content=message_text)
