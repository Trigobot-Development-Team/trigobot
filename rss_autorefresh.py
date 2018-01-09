from asyncio import sleep
from hooks.commands.rss import run as refresh_rss
import logging

async def run(client, interval = 3600):
    while True:
        logging.info('Refreshing RSS feed(s)')
        
        try:
            await refresh_rss(client)
        except Exception as err:
            logging.error('Failed to refresh feed %s' % err)

        # Go back to sleep
        await sleep(interval)