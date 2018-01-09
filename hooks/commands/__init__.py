__all__ = ['email', 'anunciar', 'rss']

# Bring all commands into this module's scope
from . import *

# TODO: add cooldown (staff unaffected)
async def run(client, message):
    if message.content.startswith('$$$'):
        parts = message.content[3:].split(" ")
        command = parts[0]

        if command in __all__:
            try:
                await eval(command).run(client, message, args=parts[1:])
            except:
                await client.send_message(message.channel, content='Erro ao executar comando')
        else:
            # TODO: be funny
            await client.send_message(message.channel, content='Comando inválido')
        
        return True
    else:
        return False