from discord import Client, Message
from ._randomness import RandomChance

# TODO: add cooldown
@RandomChance(0.001)
async def run(client: Client, message: Message) -> bool:
    if 'pestana' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='Onde é que anda o Gabi?')
    return True
