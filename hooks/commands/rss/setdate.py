from datetime import datetime
from calendar import timegm
from discord import Client, Message

import feed_state
from policy import AccessControl

SHORT_HELP_TEXT = '$$$rss setdate [nome|url] [timestamp|now|None] - \
Redefine data de última atualização para um feed'

def help(**kwargs):
    return SHORT_HELP_TEXT

def get_current_timestamp() -> int:
    return timegm(datetime.utcnow().utctimetuple())

@AccessControl(roles=['Staff'])
async def run(client: Client, message: Message, **kwargs):
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

    feed_state.update(name, new_last_update)
    message.channel.send(content='Feito')
