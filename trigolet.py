import logging
from threading import Thread
import discord
from datetime import datetime
import asyncio
logging.basicConfig(level=logging.INFO)
client = discord.Client()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	await client.send_message(357975075468607491, content="Estudassem!")


@client.event
async def on_message(message):

	if message.author == client.user:
		return

	if message.content.startswith('$$$'):
		code = message.content.split(" ")
		command = code[0]
		command = command[3:]
		if command == "email":
			await client.send_message(message.channel, content="Usem o suporte de problemas, idiotas!")
		elif command == "anunciar":
			for i in range(5):
				await client.send_message(message.channel, content= ' '.join(code[1:]))
				
	if 'pestana' in message.content.lower():
		await client.send_message(message.channel, content="Onde é que anda o Gabi?")

	elif 'mindmap' in message.content.lower():
		await client.send_message(message.channel, content="NOPAI")



client.run('MzY2Mjg2NDY4NjUxNjc5NzY1.DOZWwg.YnR8LoBL2_LGhHCIE_ydPgN67EA')
