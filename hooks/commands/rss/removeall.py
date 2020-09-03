from discord import Client, Message

import feed_state
from policy import AccessControl
from management import delete_role_channel

SHORT_HELP_TEXT = '$$$rss removeall <name> - Remove tudo o que está associado ao feed'

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
        name = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: name')

    feed_state.delete(name)
    await delete_role_channel(name)
    await message.channel.send(content='Feito')
