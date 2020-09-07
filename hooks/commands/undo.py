from management import client
from discord import Client, Message, Forbidden, NotFound
from policy import AccessControl
import logging

SHORT_HELP_TEXT = '$$$undo - Apaga última mensagem do bot no canal'

delete_mode = True

def help(**kwargs):
    """
    Shows help
    """
    return SHORT_HELP_TEXT

def is_me(message: Message) -> bool:
    """
    Check if user is author
    """
    global delete_mode

    if not delete_mode:
        return False

    if message.author == client.user:
        delete_mode = False
        return True
    return False

# Can't use in DMs because would need a lot of logic to delete
# so no need to activate relax_pm
@AccessControl(roles=['Staff'], relax_in=['justabunchofspam'])
async def run(client: Client, message: Message, **kwargs):
    """
    Run command
    """
    global delete_mode
    delete_mode = True

    try:
        await message.channel.purge(limit=100, check=is_me, bulk=False)
    except ValueError:
        pass

    # Try to delete the $$$undo call
    try:
        await message.delete()
    except (Forbidden, NotFound):
        # fail silently when you don't have permission/are using sch
        pass

    if 'sch_orig_channel' in kwargs:
        await kwargs['sch_orig_channel'].send(content='Feito')
