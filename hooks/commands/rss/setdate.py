from datetime import datetime
from calendar import timegm
from discord import Client, Message

import redis_conn
from policy import AccessControl
from .get import get_url_from_name

SHORT_HELP_TEXT = '$$$rss setdate [nome|url] [timestamp|now|None] - \
Redefine data de última atualização para um feed'

def help(**kwargs):
    return SHORT_HELP_TEXT

def get_current_timestamp() -> int:
    return timegm(datetime.utcnow().utctimetuple())

@AccessControl(roles=['Staff'])
async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()

    try:
        url = kwargs['args'][0]
    except IndexError:
        raise ValueError('Missing argument: URL/name')

    if not url.startswith('http'):
        url = await get_url_from_name(redis, url)

    try:
        new_last_update = kwargs['args'][1]
    except IndexError:
        raise ValueError('Missing argument: new time')

    if new_last_update == 'None':
        new_last_update = None
    elif new_last_update == 'now':
        new_last_update = get_current_timestamp()

    await redis.hset('feed:'+url, 'last_update', new_last_update)
    client.send_message(message.channel, content='Feito')
