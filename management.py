import discord
import json
import logging
import os
import random

from hooks import run_hooks
import rss_autorefresh

PIN_EMOJI = '📌'
PIN_MIN_REACTIONS = 5

# Current category to create channels
CHANNELS_CATEGORY = None

# @everyone role
EVERYONE = None

# Basic permissions for new roles/channels
ROLE_PERMISSIONS = None
ROLE_CHANNEL_PERMISSIONS = discord.PermissionOverwrite(view_channel=True)
EVERYONE_PERMISSIONS = discord.PermissionOverwrite(view_channel=False)

# Messages to get roles
special_messages = dict()
ROLE_EMOJI = '✋'
ROLES_CHANNEL_ID = 750825003402133524

MESSAGES_PATH = os.environ.get('TRIGOBOT_SPECIAL_MESSAGES', './messages.json')

client = discord.Client()

logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready() -> None:
    """
    Action to take when bot starts
    """
    from feed_state import init

    logging.info('We have logged in as {0.user}'.format(client))

    big_brother = discord.Game(name='https://bit.ly/BigBrotherLEIC 👀')
    await client.change_presence(activity=big_brother)

    # Default category to create channels (most recently created)
    # Important to avoid trash channels
    global CHANNELS_CATEGORY
    CHANNELS_CATEGORY = sorted(client.guilds[0].categories, \
                               key=(lambda x: x.created_at), \
                               reverse=True)[0]

    # Load messages to get role
    global special_messages
    try:
        with open(MESSAGES_PATH, "r") as f:
            special_messages = json.load(f)
    except FileNotFoundError:
        pass

    # Get @everyone role
    global EVERYONE
    EVERYONE = client.guilds[0].default_role
    global ROLE_PERMISSIONS
    ROLE_PERMISSIONS = EVERYONE.permissions

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
    if reaction.emoji == PIN_EMOJI and reaction.count >= PIN_MIN_REACTIONS and not reaction.message.pinned:
        await reaction.message.pin()

@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    """
    Action to take when a reaction is added to message (may not be in cache)
    """
    if payload.user_id == client.user.id:
        return

    guild = client.guilds[0]

    if payload.emoji.name == ROLE_EMOJI and payload.channel_id == ROLES_CHANNEL_ID:
        user = guild.get_member(payload.user_id)
        await user.add_roles(guild.get_role(special_messages[str(payload.message_id)]))

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    """
    Action to take when a reaction is removed from message (may not be in cache)
    """
    guild = client.guilds[0]

    if payload.emoji.name == ROLE_EMOJI and payload.channel_id == ROLES_CHANNEL_ID:
        user = guild.get_member(payload.user_id)
        await user.remove_roles(guild.get_role(special_messages[str(payload.message_id)]))

async def check_role_channel(feed: str) -> None:
    """
    Check if pair Role/Channel already exists and create it if not
    """
    global CHANNELS_CATEGORY
    guild = client.guilds[0]
    role = get_role(client, feed)
    channels = list(map(lambda x: x.name, CHANNELS_CATEGORY.text_channels))

    # Check role
    if role is None:
        try:
            role = await guild.create_role(name=feed, \
                                           color=discord.Colour(random.randint(0, 0xffffff)), \
                                           mentionable=True, \
                                           permissions=ROLE_PERMISSIONS)

            # Send message to receive roles
            await notify_new_role(role)
        except Exception as err:
            logging.error('Couldn\'t create role: %s' % err)
            pass

    # Check textchannel
    if feed.lower() not in channels:
        try:
            await CHANNELS_CATEGORY.create_text_channel(name=feed,
                                                        overwrites={
                                                            EVERYONE: EVERYONE_PERMISSIONS,
                                                            role: ROLE_CHANNEL_PERMISSIONS
                                                        })
        except Exception as err:
            logging.error('Couldn\'t create channel: %s' % err)
            pass

async def delete_role_channel(name: str) -> None:
    """
    Delete role, channel and special message (if exists)
    """
    low = name.lower()
    role = get_role(client, name)
    channels = dict(zip(list(map(lambda x: x.name.lower(), CHANNELS_CATEGORY.text_channels)), CHANNELS_CATEGORY.text_channels))

    if role is None:
        raise ValueError('Role %s not found' % name)

    await role.delete()
    role = role.id

    if low not in channels:
        raise ValueError('Channel %s not found' % name)

    await channels[low].delete()

    # Delete special message
    message = None
    for key, item in special_messages.items():
        if item == role:
            message = key
            break

    if message is None:
        return

    try:
        del special_messages[message]
        await (await client.guilds[0].get_channel(ROLES_CHANNEL_ID).fetch_message(int(message))).delete()
        save()
    except discord.NotFound:
        raise ValueError('Message for getting role %s not found' % name)

async def check_category(category: str) -> None:
    """
    Check if category exists and create if not
    """
    global CHANNELS_CATEGORY

    category = category.lower()

    guild = client.guilds[0]
    categories = dict(zip(list(map(lambda x: x.name.lower(), guild.categories)), guild.categories))

    if category not in categories:
        CHANNELS_CATEGORY = await guild.create_category_channel(name=category)
    else:
        CHANNELS_CATEGORY = categories[category]

async def notify_new_role(role: discord.Role) -> None:
    """
    Send special message for users to react and receive the role
    """
    channel = client.get_channel(ROLES_CHANNEL_ID)
    message = await channel.send(embed=discord.Embed(title='**[' + role.name + ']** Nova cadeira disponível', \
                          type='rich', \
                          color=role.color, \
                          description='Se vais fazer a cadeira **' + role.name + '** reage com ' + \
                                           ROLE_EMOJI + ' para teres acesso ao role ' + role.mention + ', ao canal e receberes notificações de anúncios\n Para desistires disto é só removeres a reação'))

    special_messages[str(message.id)] = role.id

    await message.add_reaction(ROLE_EMOJI )
    save()

def clear_messages() -> None:
    """
    Removes all special messages
    """
    global special_messages
    special_messages = dict()
    save()

def save() -> None:
    """
    Persist special messages data
    """
    global special_messages
    with open(MESSAGES_PATH, "w") as f:
        json.dump(special_messages, f)

def get_role(client: discord.Client, name: str) -> discord.Role:
    """
    Get role by name (None if not existent)
    """
    for role in client.guilds[0].roles:
        if role.name.lower() == name.lower():
            return role

    return None

