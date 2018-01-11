from discord import Member, Channel

import logging

def AccessControl(**kwargs):
    role_whitelist = kwargs['roles']
    relaxed_channels = kwargs.get('relax_in', [])
    relax_pm = kwargs.get('relax_pm', False)

    def _check_permission(channel: Channel, user: Member) -> bool:
        if channel.name in relaxed_channels or \
           channel.is_private:
            return True
        else:
            return user.top_role in role_whitelist

    def _decorate(fn):
        def _wrapper(*args, **kwargs):
            message = args[1]

            if _check_permission(message.channel, message.author):
                return fn(*args, **kwargs)
            else:
                raise PermissionError('Permission denied in {} to {}'.format(fn, message.author))

        return _wrapper

    return _decorate
