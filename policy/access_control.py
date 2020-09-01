from discord import Member, TextChannel
from discord.abc import PrivateChannel, GuildChannel

def check_permissions(channel: TextChannel, user: Member, **kwargs) -> bool:
    role_whitelist = kwargs['roles']
    relaxed_channels = kwargs.get('relax_in', [])
    relax_pm = kwargs.get('relax_pm', False)

    if isinstance(channel, GuildChannel) and channel.name in relaxed_channels or \
       (isinstance(channel, PrivateChannel) and user in channel.recipients and relax_pm):
        return True
    else:
        return isinstance(channel, GuildChannel) and str(user.top_role) in role_whitelist

def AccessControl(**rules):
    def _decorate(fn):
        def _wrapper(*args, **kwargs):
            message = args[1]

            user = message.author
            if 'su_orig_user' in kwargs:
                user = kwargs['su_orig_user']

            if check_permissions(message.channel, user, **rules):
                return fn(*args, **kwargs)
            else:
                raise PermissionError('Permission denied in {} to {}'.format(__name__, message.author))

        return _wrapper

    return _decorate
