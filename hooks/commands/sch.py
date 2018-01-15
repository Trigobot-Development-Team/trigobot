import logging

from copy import copy
from discord import Client, Message, Channel
from . import run_command
from .su import get_user_from_mention

SHORT_HELP_TEXT = '$$$sch [canal] [comando] - Executa comando noutro canal'

def help(**kwargs):
    return SHORT_HELP_TEXT

async def get_channel_by_name(client: Client, message: Message, name: str) -> Channel:
    # TODO: extract mention handling logic into their own functions

    if name.startswith('#'):
        name = name[1:]
        for server in client.servers:
            for channel in server.channels:
                if channel.name == name:
                    return channel

        raise ValueError('Channel not found')
    elif name.startswith('<#'):
        cid = name[2:-1]

        for channel in message.channel_mentions:
            if channel.id == cid:
                return channel

        logging.error('WTF?: Mentioned channel not found in mentions array')
        raise ValueError('Channel not found in mentions')
    else:
        # It's not a channel, it must be a user (PM)
        user = get_user_from_mention(client, message.mentions, name)

        if user is None:
            raise ValueError('User not found: {}'.format(name))

        return await client.start_private_message(user)

async def run(client: Client, message: Message, **kwargs):
    if 'sch_orig_channel' in kwargs:
        raise ValueError('You can\'t sch sch!')

    new_channel = kwargs['args'][0]
    new_channel = await get_channel_by_name(client, message, new_channel)

    # Make sure that when acting on a server we use that server's roles
    # Member != User
    if new_channel.is_private:
        author = message.author
    else:
        author = new_channel.server.get_member(message.author.id)

    # Transform message - the sch-ing
    new_message = copy(message)
    new_message.content = str.join(' ', message.content.split(' ')[2:]).lstrip()

    new_message.author = author
    new_message.channel = new_channel

    if not new_message.content.startswith('$$$'):
        new_message.content = '$$$' + new_message.content

    # Save original channel, for any error/completion messages
    kwargs['sch_orig_channel'] = message.channel

    # Re-send message through trigobot
    await run_command(client, new_message, **kwargs)
