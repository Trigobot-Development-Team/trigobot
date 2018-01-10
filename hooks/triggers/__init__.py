__all__ = ['pestana', 'mindmap', 'email', 'linux']

# Bring all trigger handlers into this module's scope
from . import *

from discord import Client, Message

# TODO: add cooldown
async def run(client: Client, message: Message) -> bool:
    for trigger in map(eval, __all__):
        if await trigger.run(client, message):
            return True

    return False
