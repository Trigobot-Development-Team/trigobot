import logging
from importlib import import_module

from discord import Client, Message
from discord.abc import GuildChannel

MODULE_LIST = ['help', 'anunciar', 'email', 'rss', 'say', 'sch', 'su', 'undo']
__all__ = MODULE_LIST

async def run_command(client: Client, message: Message, **kwargs):
    parts = message.content[3:].split(' ')
    command = parts[0]

    kwargs['args'] = parts[1:]

    author = message.author
    if 'su_orig_user' in kwargs:
        author = kwargs['su_orig_user']

    channel = message.channel
    if 'sch_orig_channel' in kwargs:
        channel = kwargs['sch_orig_channel']

    if command in MODULE_LIST:
        ch_name = "<unnamed channel>"
        if isinstance(channel, GuildChannel):
            ch_name = channel.name

        logging.info('%s called $$$%s in %s', author.name, command, ch_name)

        await import_module('.' + command, 'hooks.commands').run(client, message, **kwargs)

    else:
        raise NotImplementedError(command)

# TODO: add cooldown (staff unaffected)
async def run(client: Client, message: Message) -> bool:
    if message.content.startswith('$$$'):
        try:
            await run_command(client, message)
        except PermissionError as err:
            await message.channel.send(content='Acesso negado')
            logging.info(err)
        except NotImplementedError as err:
            await message.channel.send(content='Comando inválido: '+str(err))
        except Exception as err:
            await message.channel.send(content='Erro ao executar comando')

            # Raise the exception, let logging take care of it
            # The bot won't crash, just the handler for this message
            raise err

        return True
    else:
        return False
