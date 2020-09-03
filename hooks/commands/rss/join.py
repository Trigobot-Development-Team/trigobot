from discord import Client, Message

import feed_state

SHORT_HELP_TEXT = '$$$rss join <dados em JSON> - Adiciona feeds aos existentes atualizando os que são comuns aos dois'

def help(**kwargs) -> str:
    """
    Show help
    """
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    await feed_state.join(str.join(' ', kwargs['args']))

    await message.channel.send(content='Feeds importados com sucesso.')
