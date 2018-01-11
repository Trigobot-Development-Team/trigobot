from discord import Embed, Message, Client
import re

MSG_GNULAG_EMBED = Embed()
MSG_GNULAG_EMBED.set_image(url='https://i.redditmedia.com/BHGtcc38EEDH-9xcVl9_55QAmkX7YLIIb-qD-wsMRK0.jpg?w=1024&s=b8856843e5c2bb1b9d0f85966e6c07cc')

MSG_GNULAG_TEXT = '**@Marcelo Stallman** is gonna send you to the GNUlag if you don\'t take that back.'

GOOD_NAMES = '(gnu|linux|open.source|software.livre|free.software)'
BAD_NAMES = '(microsoft|windows|micro\\$oft|win|window\\$|proprietary)'

GOOD_ADJ = '(bom|excelente|bae|melhor|great|excellent|best|good|love|adoro)'
BAD_ADJ = '(merda|crap|bosta|shit|sucks|mau|horr(i|í)vel|fraco|bad|awful|terrible|turd)'

PATTERNS = [
    'windows( )*(>)*( )*linux',
    'linux( )*(<)*( )*windows',
    '{}(grande|[^n])*{}'.format(BAD_NAMES, GOOD_ADJ),
    '{}(grande|[^n])*{}'.format(GOOD_ADJ, BAD_NAMES),
    '{}(grande|[^n])*{}'.format(GOOD_NAMES, BAD_ADJ),
    '{}(grande|[^n])*{}'.format(BAD_NAMES, GOOD_ADJ)
]
def should_run(message: str) -> bool:
    for pattern in PATTERNS:
        if re.search(pattern, message) != None:
            print(message)
            print('matched', pattern)
            return True

    return False

async def run(client: Client, message: Message) -> bool:
    if should_run(message.content.lower()):
        await client.send_message(message.channel, \
            content = MSG_GNULAG_TEXT, embed = MSG_GNULAG_EMBED)

        return True

    return False
