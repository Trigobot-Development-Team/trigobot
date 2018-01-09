from asyncio import sleep
from hooks.commands.rss import run as refresh_rss

async def run(client, interval = 3600):
    while True:
        print('Refreshing RSS feed(s)')
        refresh_rss(client)
        await sleep(interval)