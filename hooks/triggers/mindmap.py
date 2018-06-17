from discord import Client, Message
from ._randomness import RandomChance

# TODO: add cooldown
@RandomChance(0.001)
async def run(client: Client, message: Message) -> bool:
    TRIGGERS = ['mindmap', 'mind map', 'mapa mental']
    for trigger in TRIGGERS:
        if trigger in message.content.lower():
            await client.send_message(message.channel, content='NOPAI')
            return True

    return False
