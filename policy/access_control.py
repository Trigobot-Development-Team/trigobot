from discord import Member, Channel

def check_permissions(channel: Channel, user: Member, **kwargs) -> bool:
    role_whitelist = kwargs['roles']
    relaxed_channels = kwargs.get('relax_in', [])
    relax_pm = kwargs.get('relax_pm', False)

    if channel.name in relaxed_channels or \
       (channel.is_private and user in channel.recipients and relax_pm):
        return True
    else:
        return (not channel.is_private) and user.top_role in role_whitelist

def AccessControl(**rules):
    def _decorate(fn):
        def _wrapper(*args, **kwargs):
            message = args[1]

            if check_permissions(message.channel, message.author, **rules):
                return fn(*args, **kwargs)
            else:
                raise PermissionError('Permission denied in {} to {}'.format(fn, message.author))

        return _wrapper

    return _decorate
