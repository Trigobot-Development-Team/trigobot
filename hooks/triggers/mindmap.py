from discord import Client, Message

# TODO: add cooldown
async def run(client: Client, message: Message) -> bool:
    if 'mindmap' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='NOPAI')
    return True
