from discord import Client, Message

# TODO: add cooldown
async def run(client: Client, message: Message) -> bool:
    if 'email' not in message.content.lower():
        return False

    await client.send_message(message.channel, \
                              content='Por não usares o suporte de problemas é que chumbaste, <@%s>'\
                              % message.author.id)
    return True
