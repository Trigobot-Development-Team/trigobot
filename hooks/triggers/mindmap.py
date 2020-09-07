from discord import Client, Message
from ._randomness import RandomChance

# TODO: add cooldown
@RandomChance(0.1)
async def run(client: Client, message: Message) -> bool:
    TRIGGERS = ['mindmap', 'mind map', 'mapa mental']
    for trigger in TRIGGERS:
        if trigger in message.content.lower():
            await message.channel.send(content='NOPAI')
            return True

    return False
