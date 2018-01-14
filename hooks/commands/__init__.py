__all__ = ['email', 'anunciar', 'rss', 'undo', 'say', 'help']

from discord import Client, Message
from importlib import import_module
import logging

async def run_command(client: Client, message: Message, **kwargs):
    parts = message.content[3:].split(' ')
    command = parts[0]

    kwargs['args'] = parts[1:]

    if command in __all__:
        logging.info('%s called $$$%s', message.author.display_name, command)

        await import_module('.' + command, 'hooks.commands').run(client, message, **kwargs)

    else:
        raise NotImplementedError(command)

# TODO: add cooldown (staff unaffected)
async def run(client: Client, message: Message) -> bool:
    if message.content.startswith('$$$'):
        try:
            await run_command(client, message)
        except PermissionError as err:
            await client.send_message(message.channel, content='Accesso negado')
            logging.info(err)
        except NotImplementedError as err:
            await client.send_message(message.channel, content='Comando inválido: '+str(err))
        except Exception as err:
            await client.send_message(message.channel, content='Erro ao executar comando')

            # Raise the exception, let logging take care of it
            # The bot won't crash, just the handler for this message
            raise err

        return True
    else:
        return False
