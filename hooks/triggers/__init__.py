__all__ = ['pestana', 'mindmap', 'email', 'linux', 'piazza', '_randomness']

from importlib import import_module
from discord import Client, Message

# TODO: add cooldown
async def run(client: Client, message: Message) -> bool:
    for trigger_name in __all__:
        if not trigger_name.startswith('_'):
            trigger = import_module('.' + trigger_name, 'hooks.triggers')

            if await trigger.run(client, message):
                return True

    return False
