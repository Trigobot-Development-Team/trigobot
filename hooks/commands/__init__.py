__all__ = ['email', 'anunciar']

# Bring all commands into this module's scope
from . import *

# TODO: add cooldown (staff unaffected)
async def command_hook(client, message):
    if message.content.startswith('$$$'):
        parts = message.content[3:].split(" ")
        command = parts[0]

        if command in __all__:
            await eval(command).run(client, message, args=parts[1:])
        else:
            # TODO: be funny
            await client.send_message(message.channel, content='Comando inválido')
        
        return True
    else:
        return False