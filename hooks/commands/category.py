from policy import AccessControl
from discord import Client, Message
from management import check_category

SHORT_HELP_TEXT = '$$$category [categoria] - Altera a categoria em que são criados novos canais'

def help(**kwargs) -> str:
    """
    Show help
    """
    return SHORT_HELP_TEXT

@AccessControl(roles=['Staff'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs) -> None:
    await check_category(kwargs["args"][0])
    await message.channel.send(content="Feito")
