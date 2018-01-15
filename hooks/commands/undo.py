from discord import Client, Message, Forbidden, NotFound
from policy import AccessControl
import logging

SHORT_HELP_TEXT = '$$$undo - Apaga última mensagem do bot no canal'

def help(**kwargs):
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'], relax_in=['botrequests'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    async for msg in client.logs_from(message.channel, limit=100):
        if msg.author == client.user:
            await client.delete_message(msg)
            break

    # Try to delete the $$$undo call
    try:
        await client.delete_message(message)
    except (Forbidden, NotFound):
        # fail silently when you don't have permission/are using sch
        pass

    if 'sch_orig_channel' in kwargs:
        await client.send_message(kwargs['sch_orig_channel'], content='Feito')
