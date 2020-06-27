import json

from discord import Client, Message

import redis_conn
from .add import add_feed

SHORT_HELP_TEXT = '$$$rss import - Importa lista de feeds (JSON)'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    redis = await redis_conn.get_connection()
    dump = json.loads(str.join(' ', kwargs['args']))

    counter = 0
    for feed in dump:
        try:
            await add_feed(redis, feed['name'], feed['url'], feed['last_update'])
            counter += 1
        except Exception:
            pass

    await message.channel.send(content='{} feeds adicionados com sucesso.'.format(str(counter)))
