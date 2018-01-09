async def run(client, message, **kwargs):
    await client.send_message(message.channel, \
                              content= 'Vai po caralho <@%s>' % message.author.id)