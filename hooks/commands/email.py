from discord import Client, Message

# TODO: implement cooldown
async def run(client: Client, message: Message, **kwargs):
    await client.send_message(message.channel, \
                              content='Usem o suporte de problemas, idiotas!')
