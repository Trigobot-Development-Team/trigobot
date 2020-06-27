from discord import Client, Message

async def run(client: Client, message: Message) -> bool:
    if 'http://www.wolframalpha.com/pro/' in message.content:
        await message.delete()
        return True
    else:
        return False
