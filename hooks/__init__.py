__all__ = ['commands', 'clear_wolfram', 'triggers']

# Bring all hooks into this module's scope
from . import *

async def run_hooks(client, message):
    # Runs at most one hook
    # Avoids double replieshooks
    for hook in map(eval, __all__):
        if await hook.run(client, message):
            return
