from discord import Client, Message

import feed_state

SHORT_HELP_TEXT = '$$$rss dump - Devolve backup da informação dos feeds (JSON)'

def help(**kwargs):
    """
    Show help
    """
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    msg = feed_state.dumps()

    # Split in 2000 chars' messages
    while len(msg) > 0:
        await message.channel.send(content='```\n' + msg[:1992] + '\n```')
        msg = msg[1992:]

