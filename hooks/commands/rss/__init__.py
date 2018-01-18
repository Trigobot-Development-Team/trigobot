__all__ = ['refresh', 'add', 'get', 'list', 'remove', 'setdate', 'import', 'dump']

from importlib import import_module
from discord import Client, Message

SHORT_HELP_TEXT = '$$$rss [...] - Gere feeds RSS (inclui subcomandos)'

def get_subcommand(name: str):
    return import_module('.' + name, 'hooks.commands.rss')

def get_subcommand_short_help(name: str) -> str:
    return get_subcommand(name).SHORT_HELP_TEXT

def get_subcommand_long_help(name: str, **kwargs) -> str:
    return get_subcommand(name).help(**kwargs)

def help(**kwargs):
    if not kwargs['args']:
        return str.join('\n', map(get_subcommand_short_help, __all__))
    else:
        name = kwargs['args'][0]
        kwargs['args'] = kwargs['args'][1:]
        return get_subcommand_long_help(name, **kwargs)

async def run(client: Client, message: Message = None, **kwargs):
    args = kwargs.get('args', [])
    if not args or args[0] == '':
        command = 'refresh'
    else:
        command = args[0]
        kwargs['args'] = args[1:]

    if command in __all__:
        command_module = get_subcommand(command)
        return await command_module.run(client, message, **kwargs)
    else:
        raise NotImplementedError('$$$rss {}'.format(command))
