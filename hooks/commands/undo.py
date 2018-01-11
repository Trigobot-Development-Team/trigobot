from discord import Client, Message, Forbidden
from policy import AccessControl
import logging

@AccessControl(roles=['Staff'], relax_in=['botrequests'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    async for msg in client.logs_from(message.channel, limit=100):
        if msg.author == client.user:
            await client.delete_message(msg)
            break

    # Try to delete the $$$undo call, fail silently when you don't have permission
    try:
        await client.delete_message(message)
    except Forbidden:
        pass
    except Exception as err:
        raise err
