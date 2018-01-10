# TODO: add cooldown
async def run(client, message):
    if 'mindmap' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='NOPAI')
    return True