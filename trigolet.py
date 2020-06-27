import logging
import discord
import asyncio

from hooks import run_hooks
import rss_autorefresh

PIN_MIN_REACTIONS = 3

logging.basicConfig(level=logging.INFO)
client = discord.Client()

@client.event
async def on_ready():
    logging.info('We have logged in as {0.user}'.format(client))

    big_brother = discord.CustomActivity("BigBrother@LEIC :eyes:")
    await client.change_presence(activity=big_brother)

    # RSS auto-refresh
    client.loop.create_task(rss_autorefresh.run(client))

@client.event
async def on_message(message: discord.Message):
    # Avoid answering itself
    if message.author == client.user:
        return

    await run_hooks(client, message)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if reaction.emoji == '📌' and reaction.count >= PIN_MIN_REACTIONS and not reaction.message.pinned:
        await reaction.message.pin()

if __name__ == '__main__':
    # TODO: use env variable for token, remove it from repo and regen
    client.run('MzY2Mjg2NDY4NjUxNjc5NzY1.DOZWwg.YnR8LoBL2_LGhHCIE_ydPgN67EA')
