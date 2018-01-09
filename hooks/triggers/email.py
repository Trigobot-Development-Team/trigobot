# TODO: add cooldown
async def run(client, message):
    await client.send_message(message.channel, \
                              content='Por não usares o suporte de problemas é que chumbaste, <@%s>'\
                              % message.author.id)