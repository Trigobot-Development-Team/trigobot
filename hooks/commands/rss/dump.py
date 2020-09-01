from discord import Client, Message

import feed_state

SHORT_HELP_TEXT = '$$$rss dump - Devolve backup da informação dos feeds (JSON)'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def run(client: Client, message: Message, **kwargs):
    await message.channel.send(content='```\n'+feed_state.dumps()+'\n```')
