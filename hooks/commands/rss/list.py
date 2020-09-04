from discord import Client, Message

import feed_state
from .get import format_feed

SHORT_HELP_TEXT = '$$$rss list - Lista feeds em monitorização'

def help(**kwargs):
    """
    Show help
    """
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    if len(feed_state.get_names()) == 0:
        await message.channel.send(content='Não há feeds')

    # Split in around 2000 chars' messages
    message_text = ''
    for name in feed_state.get_names():
        tmp = format_feed(name) + '\n'
        if len(message_text) + len(tmp) > 2000:
            await message.channel.send(message_text)
            message_text = tmp
        else:
            message_text += tmp

    if len(message_text) > 0:
        await message.channel.send(message_text)
