import logging
import discord
import asyncio

from hooks import run_hooks
import rss_autorefresh

logging.basicConfig(level=logging.INFO)
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # Avoid answering itself
    if message.author == client.user:
        return

    run_hooks(client, message)

# RSS auto-refresh
rss_autorefresh.run(client)

# TODO: use env variable for token, remove it from repo and regen 
client.run('MzY2Mjg2NDY4NjUxNjc5NzY1.DOZWwg.YnR8LoBL2_LGhHCIE_ydPgN67EA')
