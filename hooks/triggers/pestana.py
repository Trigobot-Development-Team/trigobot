# TODO: add cooldown
async def run(client, message):
    if 'pestana' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='Onde é que anda o Gabi?')
    return True
