async def run(client, message):
    if 'http://www.wolframalpha.com/pro/' in message.content:
        await client.delete_message(message)
        return True
    else:
        return False