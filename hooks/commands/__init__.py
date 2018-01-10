__all__ = ['email', 'anunciar', 'rss', 'undo']

# Bring all commands into this module's scope
from . import *

import logging

# TODO: add cooldown (staff unaffected)
async def run(client, message):
    if message.content.startswith('$$$'):
        parts = message.content[3:].split(" ")
        command = parts[0]

        if command in __all__:
            logging.info('{} called $$${}'.format(message.author.display_name, command))
            try:
                await eval(command).run(client, message, args=parts[1:])
            except Exception as err:
                await client.send_message(message.channel, content='Erro ao executar comando')
                raise err
        else:
            # TODO: be funny
            await client.send_message(message.channel, content='Comando inválido')
        
        return True
    else:
        return False