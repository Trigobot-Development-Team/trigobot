from importlib import import_module
from discord import Client, Message
from . import MODULE_LIST

SHORT_HELP_TEXT = str.join('\n', [
    '$$$help - Mostra ajuda sumária para todos os comandos',
    '$$$help [comando] - Mostra ajuda para um comando'
    ])

def help(**kwargs):
    return SHORT_HELP_TEXT

def get_module(name: str):
    return import_module('.' + name, 'hooks.commands')

def get_module_short_help(name: str) -> str:
    if name == 'help':
        return SHORT_HELP_TEXT
    else:
        return get_module(name).SHORT_HELP_TEXT

def get_module_long_help(name: str, **kwargs) -> str:
    if name == 'help':
        return help(**kwargs)
    else:
        return get_module(name).help(**kwargs)

async def run(client: Client, message: Message, **kwargs):
    if len(kwargs['args']) > 0:
        name = kwargs['args'][0]
        kwargs['args'] = kwargs['args'][1:]
        msg_text = get_module_long_help(name, **kwargs)
    else:
        msg_text = str.join('\n', map(get_module_short_help, MODULE_LIST))

    await message.channel.send(content=msg_text)
