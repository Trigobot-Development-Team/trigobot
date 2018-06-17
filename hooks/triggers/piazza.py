import random
from discord import Client, Message
from ._randomness import RandomChance

def get_teacher_name() -> str:
    NAMES = ['Pestana', 'Tribolet']
    return random.choice(NAMES)

# TODO: add cooldown
@RandomChance(0.001)
async def run(client: Client, message: Message) -> bool:
    if 'piazza' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='^ {} approves'.format(get_teacher_name()))
    return True
