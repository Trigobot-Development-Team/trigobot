from discord import Client, Message
import logging

import feed_state
from policy import AccessControl
from management import delete_role_channel

SHORT_HELP_TEXT = '$$$rss removeall <name(s)> - Remove tudo o que está associado ao feed'

def help(**kwargs):
    """
    Show help
    """
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    try:
        for name in kwargs['args']:
            try:
                feed_state.delete(name)
                await delete_role_channel(name)
            except:
                logging.error('No feed/role/channel named %s', name)
                pass
    except KeyError:
        raise ValueError('Missing argument: name')

    await message.channel.send(content='Feito')
