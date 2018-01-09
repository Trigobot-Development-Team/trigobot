__all__ = ['pestana', 'mindmap', 'email']

# Bring all trigger handlers into this module's scope
from . import *

# TODO: add cooldown
async def run(client, message):
    message_str = message.content.lower()
    for trigger in __all__:
        if trigger in message_str:
            await eval(trigger).run(client, message)
            return True
    
    return False