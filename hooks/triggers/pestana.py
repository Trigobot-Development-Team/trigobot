# TODO: add cooldown
async def run(client, message):
    await client.send_message(message.channel, \
                              content='Onde é que anda o Gabi?')
