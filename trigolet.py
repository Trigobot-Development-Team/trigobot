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


@client.event
async def on_message(message):

	if message.author == client.user:
		#avoid answering to own answers
		return

	if message.content.startswith('$$$'):
		code = message.content.split(" ")
		command = code[0]
		command = command[3:]
		#excludes the $$$ from command
		if command == "email":
			await client.send_message(message.channel, content="Usem o suporte \
			de problemas, idiotas!")
		elif command == "anunciar":
				await client.send_message(message.channel, content= 'Vai po \
				caralho <@%s>' % message.author.id)

	elif 'pestana' in message.content.lower():
		await client.send_message(message.channel, \
		content="Onde é que anda o Gabi?")

	elif 'mindmap' in message.content.lower():
		await client.send_message(message.channel, \
		content="NOPAI")
	elif 'email' in message.content.lower():
		await client.send_message(message.channel, content='Por não usares o \
		suporte de problemas é que chumbaste, <@%s>' % message.author.id)

	if 'http://www.wolframalpha.com/pro/' in message.content:
		await client.delete_message(message)


client.run('MzY2Mjg2NDY4NjUxNjc5NzY1.DOZWwg.YnR8LoBL2_LGhHCIE_ydPgN67EA')
