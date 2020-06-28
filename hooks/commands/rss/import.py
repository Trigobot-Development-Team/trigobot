from discord import Client, Message

import feed_state

SHORT_HELP_TEXT = '$$$rss import <dados em JSON> - Importa lista de feeds substituindo os existentes'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    feed_state.loads(str.join(' ', kwargs['args']))

    await message.channel.send(content='Feeds importados com sucesso.')
