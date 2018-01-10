import logging
import discord
import asyncio

from hooks import run_hooks
import rss_autorefresh

logging.basicConfig(level=logging.INFO)
client = discord.Client()

@client.event
async def on_ready():
    logging.info('We have logged in as {0.user}'.format(client))

    big_brother = discord.Game()
    big_brother.name = 'bit.ly/BigBrotherLEIC'
    big_brother.url = 'https://bit.ly/BigBrotherLEIC'
    await client.change_presence(game=big_brother)

    # RSS auto-refresh - blocks on_ready callback
    await rss_autorefresh.run(client)

@client.event
async def on_message(message: discord.Message):
    # Avoid answering itself
    if message.author == client.user:
        return

    await run_hooks(client, message)

if __name__ == '__main__':
    # TODO: use env variable for token, remove it from repo and regen
    client.run('MzY2Mjg2NDY4NjUxNjc5NzY1.DOZWwg.YnR8LoBL2_LGhHCIE_ydPgN67EA')
