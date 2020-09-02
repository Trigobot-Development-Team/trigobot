import discord
import logging
import random

from hooks import run_hooks
import rss_autorefresh

PIN_MIN_REACTIONS = 1

# Current category to create channels
CHANNELS_CATEGORY = discord.CategoryChannel

client = discord.Client()

logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready() -> None:
    """
    Action to take when bot starts
    """
    from feed_state import init

    logging.info('We have logged in as {0.user}'.format(client))

    big_brother = discord.Game("BigBrother@LEIC :eyes:")
    await client.change_presence(activity=big_brother)

    # Default category to create channels
    # Important to avoid trash channels
    await client.loop.create_task(set_recent_category())

    # RSS initialization
    # Needs async to create roles/channels
    await client.loop.create_task(init())

    # RSS auto-refresh
    client.loop.create_task(rss_autorefresh.run(client))

@client.event
async def on_message(message: discord.Message) -> None:
    """
    Action to take when a message is published
    """

    # Avoid answering itself
    if message.author == client.user:
        return

    await run_hooks(client, message)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    """
    Action to take when a reaction is added to a message
    """
    if reaction.emoji == '📌' and reaction.count >= PIN_MIN_REACTIONS and not reaction.message.pinned:
        await reaction.message.pin()

async def check_role_channel(feed: str) -> None:
    """
    Check if pair Role/Channel already exists and create it if not
    """
    global CHANNELS_CATEGORY
    guild = client.guilds[0]
    roles = list(map(lambda x: x.name, guild.roles))
    channels = list(map(lambda x: x.name, CHANNELS_CATEGORY.text_channels))

    # Check role
    if feed not in roles:
        try:
            role = await guild.create_role(name=feed, color=discord.Colour(random.randint(0, 0xffffff)), mentionable=True)
        except Exception as err:
            logging.error("Couldn't create role: %s" % err)
            pass

    # Check textchannel
    if feed.lower() not in channels:
        try:
            await CHANNELS_CATEGORY.create_text_channel(name=feed)
        except Exception as err:
            logging.error("Couldn't create channel: %s" % err)
            pass

async def check_category(category: str) -> None:
    """
    Check if category exists and create it if not
    """
    global CHANNELS_CATEGORY

    category = category.lower()

    guild = client.guilds[0]
    categories = dict(zip(list(map(lambda x: x.name.lower(), guild.categories)), guild.categories))

    if category not in categories:
        CHANNELS_CATEGORY = await guild.create_category_channel(name=category)
    else:
        CHANNELS_CATEGORY = categories[category]

async def set_recent_category() -> None:
    """
    Set the category to the most recently created
    """
    global CHANNELS_CATEGORY
    CHANNELS_CATEGORY = sorted(list(client.guilds[0].categories), key=(lambda x: x.created_at), reverse=True)[0]
