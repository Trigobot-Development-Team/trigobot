__all__ = ['pestana', 'mindmap', 'email', 'linux']

# Bring all trigger handlers into this module's scope
from . import *

# TODO: add cooldown
async def run(client, message):
    for trigger in map(eval, __all__):
        if await trigger.run(client, message):
            return True

    return False
