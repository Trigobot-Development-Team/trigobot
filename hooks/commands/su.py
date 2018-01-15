from copy import copy
from discord import Client, Message, User
from policy import AccessControl
from . import run_command

SHORT_HELP_TEXT = '$$$su [utilizador] [comando] - Executa comando como outro utilizador'

def help(**kwargs):
    return SHORT_HELP_TEXT

def get_user_by_name(client: Client, name: str) -> User:
    for member in client.get_all_members():
        if member.name == name:
            return member

    raise ValueError('Member not found')

def get_user_by_id(client: Client, mentions: list, uid: str) -> User:
    for user in mentions:
        if user.id == uid:
            return user

    for member in client.get_all_members():
        if member.id == uid:
            return member

    return client.get_user_info(uid)

def get_user_from_mention(client: Client, mentions: list, mention: str) -> User:
    if mention.startswith('@'):
        name = mention[1:]

        return get_user_by_name(client, name)
    elif mention.startswith('<@'):
        name = mention[2:-1]

        # When mentioning by nickname, Discord adds a ! before the ID
        if name[0] == '!':
            name = name[1:]

        return get_user_by_id(client, mentions, name)

@AccessControl(roles=['Staff'], relax_in=['botrequests'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    if 'su_orig_user' in kwargs:
        raise ValueError('You can\'t su su')

    new_user_name = kwargs['args'][0]

    new_user = get_user_from_mention(client, message.mentions, new_user_name)
    if new_user is None:
        raise ValueError('Unknown user "{}"'.format(new_user_name))

    # Create a changed message, to execute as a command
    new_message = copy(message)
    new_message.author = new_user
    new_message.content = str.join(' ', kwargs['args'][1:]).lstrip()

    if not new_message.content.startswith('$$$'):
        new_message.content = '$$$' + new_message.content

    # Save original user, to respect permissions
    kwargs['su_orig_user'] = message.author

    await run_command(client, new_message, **kwargs)
