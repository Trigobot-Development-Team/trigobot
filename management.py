import discord
import json
import logging
import os
import random

from hooks import run_hooks
import rss_autorefresh

PIN_EMOJI = '📌'
PIN_MIN_REACTIONS = 5

# To enforce rules
RULES_CHANNEL = 757603395799482478
GENERAL_CHANNEL = 357975722029219850

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
ROLES_CHANNEL_ID = 751508970308632757

MESSAGES_PATH = os.environ.get('TRIGOBOT_SPECIAL_MESSAGES', './messages.json')

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = False
intents.bans = False
intents.emojis = False
intents.integrations = False
intents.webhooks = False
intents.invites = False
intents.voice_states = False
intents.presences = False
intents.messages = True
intents.guild_messages = True
intents.dm_messages = True
intents.reactions = True
intents.guild_reactions = True
intents.dm_reactions = True
intents.typing = False
intents.guild_typing = False
intents.dm_typing = False
client = discord.Client(intents=intents)

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
async def on_member_join(member: discord.Member):
    """
    Action to take when a member joins the server
    """
    dm = member.dm_channel
    if dm == None:
        dm = await member.create_dm()

    try:
        message = "**[PT]**\n\nBem vindo ao servidor de MEIC\n\n" + \
            "Temos algumas instruções que deves seguir para melhor interagires com os outros membros e para teres uma melhor experiência no Técnico\n**INSTRUÇÕES:**\n" + \
            "Vai ao canal **#registration** e inscreve-te nas cadeiras que vais fazer reagindo às respetivas mensagens do bot com :raised_hand: (podes desinscrever-te ou reinscrever-te a qualquer momento removendo/readicionando a reação)\n" + \
            "Isto dar-te-á acesso ao role de cada cadeira (e ao respetivo canal), e esse role será taggado nos anúncios do Fénix dessa cadeira publicados em **#info-importante** (podes dar mute à vontade, porque vais receber notificação quando o anúncio for de uma das tuas cadeiras)\n\n" + \
            "E temos também algumas regras para o bom funcionamento do servidor\n**REGRAS:**\n" + \
            "0. Tenta organizar-te, isto é, assuntos relacionados com o tema X são discutidos no canal X\n" + \
            "1. Muda o nick de forma a que os outros te consigam reconhecer, por exemplo, <primeiro nome> <apelido>, o Discord deixa-te ter um nick diferente para cada servidor, por isso não perdes o teu nick original\n" + \
            "2. Assuntos de cadeiras são discutidos nos canais das cadeiras, não faças spam no **#general** com pedidos de grupos/elementos para grupo\n" + \
            "3. Se há membros estrangeiros num canal, escreve em inglês (pelo menos nos canais das cadeiras)\n" + \
            "4. Usa menções a roles das cadeiras (@<nome cadeira>) em vez de (@​here/@​everyone) a não ser que precises mesmo de chamar o @​Staff ao barulho\n" + \
            "\nPergunta à vontade, alguém será capaz de te ajudar :wink:"

        await dm.send(content=message)

        message = "**[EN]**\n\nWelcome to the MEIC server\n\n" + \
            "We have a few instructions that you should follow in order to better interact with the other members and for you to have a better experience in Técnico\n**INSTRUCTIONS:**\n" + \
            "Go to **#registration** and sign up for your courses by reacting to their respective messages with :raised_hand: (you can remove/add the reaction at any time to undo/redo this action).\n" + \
            "This will give you access to the course's role (and respective channel). That role will be tagged in the course's Fénix announcements published in **#info-importante** (feel free to mute this channel as you will receive notifications from your course's announcements)\n\n" + \
            "We also have a few rules to ensure the smooth operation of the server\n**RULES:**\n" + \
            "0. Try to organize your conversations. Topic X should be discussed inside channel X\n" + \
            "1. Change your nickname to something others can recognize (e.g. <firstname> <lastname>). Discord allows you to have a different nickname for server, so, your original nickname is kept in the other servers\n" + \
            "2. Course talks goes to course channels: don't spam **#general** with group paring stuff\n" + \
            "3. If there are non-portuguese speakers in a channel, please use english\n" + \
            "4. Use course role mentions (@<course name>) instead of the general ones (@​all/@​everyone/...), unless you really need @​Staff to hear about it\n" + \
            "\nFeel free to ask, someone might be able to help you :wink:"

        await dm.send(content=message)
    except discord.Forbidden:
        # Case user has DMs disabled for server members
        channel = client.get_channel(GENERAL_CHANNEL)
        message = "Hey " + member.mention + "\nCheck channel " + client.get_channel(RULES_CHANNEL).mention
        await channel.send(content=message)


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
    """
    Action to take when a reaction is added to a message
    """
    if reaction.emoji == PIN_EMOJI and reaction.count >= PIN_MIN_REACTIONS and not reaction.message.pinned:
        await reaction.message.pin(reason="the people have spoken")

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
    channels = list(map(lambda x: x.name, guild.text_channels))

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
        await (await client.guilds[0].get_channel(ROLES_CHANNEL_ID).fetch_message(int(message))).delete()
        del special_messages[message]
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
    react_description  = '**[PT]**\n\nSe vais fazer a cadeira **' + role.name + '** reage com ' + \
        ROLE_EMOJI + ' para teres acesso ao role ' + role.mention + ', ao canal e receberes notificações de anúncios\n Para desistires disto é só removeres a reação\n\n'
    react_description += '**[EN]**\n\nIf you\'re enrolling in **' + role.name + '** react with ' + \
        ROLE_EMOJI + ' to get access to the role ' + role.mention + ', to the channel and to receive notifications\n To quit, just remove the reaction'
    channel = client.get_channel(ROLES_CHANNEL_ID)
    message = await channel.send(embed=discord.Embed(title='**[' + role.name + ']** Nova cadeira disponível', \
                          type='rich', \
                          color=role.color, \
                          description=react_description))

    special_messages[str(message.id)] = role.id

    await message.add_reaction(ROLE_EMOJI)
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

