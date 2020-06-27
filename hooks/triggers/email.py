from discord import Client, Message
from ._randomness import RandomChance

# TODO: add cooldown
@RandomChance(0.001)
async def run(client: Client, message: Message) -> bool:
    if 'mail' not in message.content.lower():
        return False

    await message.channel.send( \
                                content='Por não usares o suporte de problemas é que chumbaste, <@%s>'\
                              % message.author.id)
    return True
