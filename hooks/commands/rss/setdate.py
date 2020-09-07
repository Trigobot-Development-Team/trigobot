from datetime import datetime
from calendar import timegm
from discord import Client, Message

import feed_state
from policy import AccessControl

SHORT_HELP_TEXT = '$$$rss setdate [nome|url] [timestamp|now|None] - \
Redefine data de última atualização para um feed'

def help(**kwargs):
    """
    Show help
    """
    return SHORT_HELP_TEXT

def get_current_timestamp() -> int:
    """
    Get current timestamp (UTC)
    """
    return timegm(datetime.utcnow().utctimetuple())

@AccessControl(roles=['Staff'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    """
    Run commands
    """
    try:
        name = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: name')

    try:
        new_last_update = kwargs['args'][1]
    except IndexError:
        raise ValueError('Missing argument: new time')

    if new_last_update == 'None':
        new_last_update = None
    elif new_last_update == 'now':
        new_last_update = get_current_timestamp()
    else:
        new_last_update = int(new_last_update)

    feed_state.update(name, new_last_update)
    await message.channel.send(content='Feito')
