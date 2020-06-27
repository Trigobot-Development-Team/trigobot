from discord import Client, Message

SHORT_HELP_TEXT = '$$$anunciar - Anuncia-te ao mundo com classe'

def help(**kwargs):
    return SHORT_HELP_TEXT

# TODO: implement cooldown
async def run(client: Client, message: Message, **kwargs):
    await message.channel.send(content= 'Vai po caralho <@%s>' % message.author.id)
