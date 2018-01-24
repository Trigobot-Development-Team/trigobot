from discord import Client, Message

# TODO: add cooldown
async def run(client: Client, message: Message) -> bool:
    TRIGGERS = ['mindmap', 'mind map', 'mapa mental']
    for trigger in TRIGGERS:
        if trigger in message.content.lower():
            await client.send_message(message.channel, content='NOPAI')
            return True

    return False
