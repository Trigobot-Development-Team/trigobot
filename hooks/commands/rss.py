import re
import json
import feedparser

def strip_html(s):
    return re.sub('<[^<]+?>|\\xa0|&#34;', '', s)

def format_feed_entry(feed_name, entry):
    # TODO: convert HTML to Markdown for readability
    # TODO: shorten link(s) (?)
    return '{} {} \n{}\n'.format(feed_name, entry['link'], \
                                 strip_html(entry['summary']))

async def run(client, message = None):
    # TODO: Use a proper DB (Redis?) for optimized I/O
    f = open('feeds.json')
    feeds = json.load(f)
    f.close()

    new_feeds = []          # New json data to dump after fetching
    msg = ''

    for feed in feeds:
        data = feedparser.parse(feed['link'])

        for entry in data['entries']:
            if feed['time'] == None or \
                list(entry['published_parsed']) > feed['time']:
                # TODO: consider calling client.send_message without await
                #       instead of constructing a big message in memory
                msg += format_feed_entry(feed['name'], entry)
            else:
                break

        feed['time'] = data['entries'][0]['published_parsed'] # Most recent date
        new_feeds.append(feed)

    f = open('feeds.json', 'w')
    json.dump(new_feeds, f)
    f.close()

    await client.send_message(message.channel, content=msg)