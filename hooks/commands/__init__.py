__all__ = ['email', 'anunciar', 'rss', 'undo', 'say', 'help']

# Bring all commands into this module's scope
from . import *

from discord import Client, Message
import logging

# TODO: add cooldown (staff unaffected)
async def run(client: Client, message: Message) -> bool:
    if message.content.startswith('$$$'):
        parts = message.content[3:].split(" ")
        command = parts[0]

        if command in __all__:
            logging.info('{} called $$${}'.format(message.author.display_name, command))
            try:
                await eval(command).run(client, message, args=parts[1:])
            except PermissionError as err:
                await client.send_message(message.channel, content='Accesso negado')
                logging.info(err)
            except Exception as err:
                await client.send_message(message.channel, content='Erro ao executar comando')

                # Raise the exception, let logging take care of it
                # The bot won't crash, just the handler for this message
                raise err
        else:
            # TODO: be funny
            await client.send_message(message.channel, content='Comando inválido')

        return True
    else:
        return False
