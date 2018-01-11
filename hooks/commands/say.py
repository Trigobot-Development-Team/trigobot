from discord import Client, Message, Channel, User, Embed
from policy import check_permissions

def get_user_by_name(client: Client, name: str) -> User:
    for server in client.servers:
        for member in server.members:
            if member.name == name:
                return member

    raise ValueError('Member not found')

async def get_channel_by_name(client: Client, user: User, name: str) -> Channel:
    if name.startswith('#'):
        name = name[1:]
        for server in client.servers:
            for channel in server.channels:
                if channel.name == name:
                    return channel

        raise ValueError('Channel not found')
    elif name.startswith('@'):
        name = name[1:]
        user = get_user_by_name(client, name)
        return await client.start_private_message(user)


RBAC_RULES = dict(roles=['Staff'], relax_in=['botrequests'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    destination = kwargs['args'][0]
    if destination == 'here':
        destination = message.channel
    else:
        destination = await get_channel_by_name(client, message.author, destination)

    msg_content = str.join(' ', kwargs['args'][1:])

    # Make sure that when acting on a server we use that server's roles
    if destination.is_private:
        user = message.author
    else:
        user = destination.server.get_member(message.author.id)

    if check_permissions(destination, user, **RBAC_RULES):
        await client.send_message(destination, content=msg_content)

        if message.channel != destination:
            await client.send_message(message.channel, content='Feito')
    else:
        raise PermissionError('Permission denied to {} in $$$say'.format(message.author.display_name))
