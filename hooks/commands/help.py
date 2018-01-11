from discord import Client, Message

# TODO: each command should specify its own help text
HELP_TEXT=str.join('\n', [
    '$$$help - Mostra ajuda',
    '$$$email, $$$anunciar - Fun',
    '$$$rss - Força atualização dos feeds',
    '$$$undo - Remove última resposta do bot (no canal atual) (Staff only, excepto em PMs e #botrequests)',
    '$$$say (@nick|#canal|here) (mensagem) - Faz o bot dizer alguma coisa (Staff only, excepto em PMs e #botrequests'
])

async def run(client: Client, message: Message, **kwargs):
    # TODO: distinguish between $$$help and $$$help <command>
    await client.send_message(message.channel, content=HELP_TEXT)
