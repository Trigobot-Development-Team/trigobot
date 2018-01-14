from discord import Client, Message
from policy import AccessControl
import re

@AccessControl(roles=['Staff'], relax_in=['botrequests'], relax_pm=True)
async def run(client: Client, message: Message, **kwargs):
    msg_content = str.join(' ', kwargs['args'])
    p = re.compile('@\\w+#\\d{4}') # regex expression for mention
    user_mentions = p.findall(msg_content)
    if not user_mentions == []:
        for usr in user_mentions:
            msg_content.replace(usr, '<@%s>' % usr[1:]) # fix mentions

    await client.send_message(message.channel, content=msg_content)

    if 'sch_orig_channel' in kwargs:
        await client.send_message(kwargs['sch_orig_channel'], content='Feito')
