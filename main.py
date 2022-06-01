import discord, requests, json, os
from discord.ext import commands, tasks
# from keep_alive import keep_alive
from utils.protocols import is_valid_account_number  # importing the method for checking if an account number is valid
from utils.discord import send_embed, send_verification_message  # importing the method for sending the embed to show an error message, importing random  number generator
from pymongo import MongoClient  # importing the module to get a connection to database mongo
from config.settings import MONGO_DB_NAME, MONGO_CLIENT_ADDRESS, MONGO_HOST, MONGO_PORT, BANK_IP, BANK_PROTOCOL, BOT_ACCOUNT_NUMBER, MAXIMUM_CONFIRMATION_CHECKS, ETHER_VALUE  # importing database host and port address and name and bank detials
from utils.network import fetch, make_api_url  # to fetch url and convert it into python object
import pymongo
from pymongo.errors import DuplicateKeyError


# enable intents(to get info about members)
intents = discord.Intents.default()
intents.members = True  # member intents


client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')


mongo = MongoClient(MONGO_CLIENT_ADDRESS)
database = mongo[MONGO_DB_NAME]

"""client = pymongo.MongoClient("mongodb+srv://usamasaleem:usamasaleem@discord-bot.pg0f5.mongodb.net/?retryWrites=true&w=majority")
database = client.test"""


DEPOSITS = database['deposits']
REGISTRATIONS = database['registrations']
USERS = database['users']


"""get_address_url = make_api_url("account", "balance", BOT_ACCOUNT_NUMBER, tag="latest")
print(get_address_url)"""

def check_confirmations():  # query unconfirmed deposits from database/mongodb, check bank for confirmation status

    unconfirmed_deposits = DEPOSITS.find({
        'is_confirmed': False
    })

    for deposit in unconfirmed_deposits:
        """
        try:

            "response = requests.get(url)
            if response.status_code == 200:
                if response.json()["count"] > 0:
                    confirmations = True
                    message = "Transaction confirmed!"
                else:
                    message = "Transaction not confirmed!""
"""
        try:
            confirmations = True
            if confirmations:  # handle deposit confirmations
                # print(f'{confirmations} okay') # to check for if confirmation is True or false
                handle_deposit_confirmation(deposit=deposit)

        except Exception:
            pass

      #  increment_confirmation_checks(deposit=deposit)


def check_deposits():  # fetch bank transactions from bank, Insert new deposits into database

    next_url = make_api_url("account", "txlist", BOT_ACCOUNT_NUMBER, sort="desc", startblock=0, endblock=99999999, page=1, offset=10000)

    data = fetch(url=next_url, headers={})

    bank_transactions = data['result']

    for bank_transactions in bank_transactions:
        try:
            DEPOSITS.insert_one({
                '_id': bank_transactions['hash'],
                'blockNumber': bank_transactions['blockNumber'],
                'signature_hash': bank_transactions['hash'],
                'amount': int(bank_transactions['value']) / ETHER_VALUE,
                'is_confirmed': False,
                'sender': bank_transactions['from'],
                'to': bank_transactions['to']
            })
        except DuplicateKeyError:
            break


def handle_deposit_confirmation(*, deposit):  # update confirmation status of deposit, increase user balance or create new user if they don't already exist

    DEPOSITS.update_one(
        {'_id': deposit['_id']},
        {
            '$set': {
                'is_confirmed': True
            }
        }
    )

    registration = REGISTRATIONS.find_one({
        'account_number': deposit['sender']
    })
    if registration:
        handle_registration(registration=registration)
    else:
        USERS.update_one(
            {'account_number': deposit['sender']},
            {
                '$inc': {
                    'balance': deposit['amount']
                }
            }
        )


def handle_registration(*, registration):  # ensure account number is not already registered, create a new user or update the account number of existing user

    discord_user_id = registration['_id']
    account_number_registered = bool(USERS.find_one({'account_number': registration['account_number']}))

    if not account_number_registered:
        existing_user = USERS.find_one({'_id': discord_user_id})

        if existing_user:
            USERS.update_one(
                {'_id': discord_user_id},
                {
                    '$set':{
                        'account_number': registration['account_number']
                    }
                }
            )
        else:
            results = USERS.insert_one({'_id': discord_user_id,
                             'account_number': registration['account_number'],
                             'balance': 0
                                        })

            REGISTRATIONS.delete_one({'_id': discord_user_id})


            """if results.modified_count:
                send_user_register_confirmation()"""



"""
async def send_user_register_confirmation(ctx):
    await send_embed(
        ctx=ctx,
        title='Registration Updated.',
        description=(
            'Your registration has been updated.'
            'To complete registration, follow the instruction sent via DM.'
        )
    )
"""


def increment_confirmation_checks(*, deposit):  # increments the number of confirmation checks for given deposits

    DEPOSITS.update_one(
        {'_id': deposit['_id']},
        {
            '$inc': {
                'confirmation_checks': 1
            }
        }
    )

@tasks.loop(seconds=5.0)
async def poll_blockchain():  # poll blockchain for new transactions/deposits sent to the bot account, ONLY accept confirmed transactions
    check_deposits()
    check_confirmations()

@client.event
async def on_ready():
    print("I'm back online")
    poll_blockchain.start()


badwords = ['bad', 'words', 'here']
# emojis dictionary
emojis = {'grinning': '\U0001F600', 'cool': '\U0001F60E', 'cowboy': '\U0001F920'}
poll = {'poll:': 'polling:'}

@client.event
async def on_message(message):  # responding to messages
    if message.author == client.user:
        return
    author_id = message.author.id
    # RESPONDING TO MESSAGES I.E., AUTO-MODERATION AND HELP -> STARTING
    word = message.content
    lower_c = word.lower()
    res = lower_c.split()
    """
    check_bad = 0
    for bad_word in res:
        if bad_word in badwords:
            check_bad = 1
            break
        else:
            check_bad = 0"""
    delKeyword = "!delword"
    if ((message.author.id != 810408611573661726)):
        with open("black list record.json") as json_file:
            data = json.load(json_file)
        for key in data:
            if ((data[key] in message.content) and (delKeyword not in message.content)):
                channel = client.get_channel(980718921533493299)  # logs channel id
                warnn = f"**Profanity Alert**: {message.author.mention} just said: ||"
                content = message.content
                hide = "||"
                conn = warnn + content + hide
                """await message.delete()
                await message.channel.send(f"**Profanity Alert**: {message.author.mention} Don't use that word here!")
                await channel.send(conn)"""
                with open("warnings.json") as json_file:
                    data_w = json.load(json_file)
                    for k in data_w.keys():
                        if int(k) == author_id:
                            if (data_w[k]) < 3:
                                await message.channel.send(f"**Profanity Alert**: {message.author.mention} Don't use that word here! This is your warning no. {data_w[k]+1}/3.")
                                default_val = data_w[k]
                                break
                            else:
                                # await member.kick(reason="You have reached your warning limits, you will be kicked now for ignoring the rules of this server.")
                                if author_id == 702004040669855825:
                                    await message.channel.send("I know you are the server owner so i don't have the permission to kick you, but please i beg stop swearing <:prayel:980393950231805962>")
                                    break
                                else:
                                    await message.channel.send(f"**Profanity Alert**: {message.author.mention} You have reached your warning limits, you will be kicked now for ignoring the rules of this server.")
                                    await message.author.kick(reason="You have reached your warning limits, you will now be kicked for ignoring the rules of this server.")
                                    default_val = 0
                                    break
                        else:
                            default_val = 0
                    if default_val == 0:
                        await message.channel.send(f"**Profanity Alert**: {message.author.mention} Don't use that word here! This is your warning number {default_val + 1}/3.")
                    data_w.update({str(author_id): default_val+1})
                    j = json.dumps(data_w)
                    with open('warnings.json', 'w') as f:
                        f.write(j)
                        f.close()
                await channel.send(conn)
                await message.delete()
                # client.dispatch('profanities', message, bad_word)



    for i in res:  # message reaction and poll
        if i in emojis:
            emoji = i
            unicode = emojis[emoji]
            await message.add_reaction(unicode)
    for i in res:
        if i in poll:
            await message.add_reaction('\U00002705')
            await message.add_reaction('\U0000274C')
    await client.process_commands(message)  # to process commands from the same message
    # RESPONDING TO MESSAGES I.E., AUTO-MODERATION AND HELP -> END

# REACTIONS AND MESSAGE EDITS I.E., ROLES AND MESSAGE EDITS -> STARTING

# message edits


@client.event
async def on_message_edit(before, after):  # see message edit history
    if before.author == client.user:
        return
    await before.channel.send(
        f'{before.author} edited their message.\n\n'
        f'Before: **{before.content}\n**'
        f'After: **{after.content}\n**'
    )

# user reaction to messages


@client.event
async def on_reaction_add(reaction, user):  # emoji reaction to messages

    if user == client.user:
        return
    await reaction.message.channel.send(f'{user} reacted with {reaction.emoji} on **{reaction.message.content}**')
# REACTIONS AND MESSAGE EDITS I.E., ROLES AND MESSAGE EDITS -> END

# ROLES BOT I.E., Giving custom roles -> STARTING


@client.event
async def on_raw_reaction_add(payload):  # Add custom roles

    target_message_id = 980723247748374548
    if payload.message_id != target_message_id:
        return

    guild = client.get_guild(payload.guild_id)  # Get server information/id

    if payload.emoji.name == '📕':
        role = discord.utils.get(guild.roles, name='Study')
        await payload.member.add_roles(role)
    elif payload.emoji.name == '🔴':
        role = discord.utils.get(guild.roles, name='Streamer')
        await payload.member.add_roles(role)
    elif payload.emoji.name == '👨‍🏫':
        role = discord.utils.get(guild.roles, name='Teacher')
        await payload.member.add_roles(role)
    elif payload.emoji.name == '🎮':
        role = discord.utils.get(guild.roles, name='Gaming')
        await payload.member.add_roles(role)
    elif payload.emoji.name == '🧑‍🎓':
        role = discord.utils.get(guild.roles, name='Student')
        await payload.member.add_roles(role)

@client.event
async def on_raw_reaction_remove(payload):  # Remove custom roles

    target_message_id = 980723247748374548
    if payload.message_id != target_message_id:
        return

    guild = client.get_guild(payload.guild_id)  # Get server information/id
    member = guild.get_member(payload.user_id)
    if payload.emoji.name == '📕':
        role = discord.utils.get(guild.roles, name='Study')
        await member.remove_roles(role)
    elif payload.emoji.name == '🔴':
        role = discord.utils.get(guild.roles, name='Streamer')
        await member.remove_roles(role)
    elif payload.emoji.name == '👨‍🏫':
        role = discord.utils.get(guild.roles, name='Teacher')
        await member.remove_roles(role)
    elif payload.emoji.name == '🎮':
        role = discord.utils.get(guild.roles, name='Gaming')
        await member.remove_roles(role)
    elif payload.emoji.name == '🧑‍🎓':
        role = discord.utils.get(guild.roles, name='Student')
        await member.remove_roles(role)

# ROLES BOT I.E., Giving custom roles -> END

# CUSTOM COMMANDS/HELP AND EMBEDS I.E., Making custom commands,help commands etc. -> STARTING


@client.command()
async def addword(ctx, word):  # to add more bad words to the black list dictionary(in json file)
    with open("numbers.json") as json_file:
        keys = "number"
        data = json.load(json_file)
        number_c = data['number']
        data.update({keys: number_c + 1})
        # print(data)
        j = json.dumps(data)
        with open('numbers.json', 'w') as f:
            f.write(j)
            f.close()
        next_num = number_c + 1

    with open("black list record.json") as json_file:
        keys = "word"
        data = json.load(json_file)
        data.update({keys + str(next_num): word})
        # print(data)
        """temp = data["blacklist"]
        y = {keys: word}
        temp.append(y)
        write_json(data)"""
        j = json.dumps(data)
        with open('black list record.json', 'w') as f:
            f.write(j)
            f.close()
    await ctx.message.channel.send("|| " + word + " || has been added to the filter.")
    await ctx.message.delete()


@client.command()
async def delword(ctx, word):  # removes a word from the blacklist

    with open("black list record.json") as json_file:
        data = json.load(json_file)
    for key in data:
        if (data[key] in word):
            break
    del data[key]
    j = json.dumps(data)
    with open('black list record.json', 'w') as f:
        f.write(j)
        f.close()
    # blacklist.remove(word)
    # blacklist.remove(word)
    await ctx.message.channel.send("|| " + word + " || has been removed from the filter.")
    await ctx.message.delete()


@client.command()
async def remove(ctx, amount=0):  # purges an amount of messages
    await ctx.channel.purge(limit=amount + 1)
    # channel = client.get_channel(810409079481696299)
    await ctx.message.channel.send(str(amount) + " messages were removed.")



@client.command()
async def wordlist(ctx):  # sends blacklisted words to user
    with open("black list record.json") as json_file:
        data = json.load(json_file)
        black_list_show = []
        for key in data:
            black_list_show.append(data[key])
    channel = client.get_channel(980718921533493299)  # logs channel id
    await ctx.message.channel.send("The list of blacklisted words has been sent to the logs channel!")
    await channel.send("The blacklisted words are:|| " + str(black_list_show) + " ||")



@client.command()
async def mod_commands(ctx, user: discord.member = None):  # sends list of commands to user
    if user is None:
        user = ctx.author

    embed = discord.Embed(
        title='Moderator Commands',
        description='Welcome to the help section of moderator-only commands. Here is the list and explanation for all the commands that are specifically for moderators.',
        color=discord.Colour.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)

    embed.add_field(
        name='!addword',
        value='Adds another word to the list of blacklisted words to filter out when chatting.',
        inline=True
    )
    embed.add_field(
        name='!delword',
        value='Deletes the word from the blacklist.(Takes a word as an argument.)',
        inline=True
    )
    embed.add_field(
        name='!wordlist',
        value='Show the list of blacklisted words in the #logging channel.',
        inline=True
    )
    embed.add_field(
        name='!remove',
        value='Removes number of messages that moderator or server owner wants to.(Takes an integer as an argument.)',
        inline=True
    )

    await ctx.send(embed=embed)
    """await ctx.author.send("The commands offered are: \n!addWord (word) - adds desired word to the blacklist \n!delWord (word) - removes desired word from the blacklist\n"
                          "!wordList - presents the list of words blacklisted\n"
                          "!remove (#) - removes desired number of messages from the chat\n!commands - provides the list of available commands")"""


@client.command()
async def help(ctx, user:discord.member=None):  # Help embed i.e., shows all commands

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title='Bot Commands',
        description='Welcome to the help section. Here are all the commands for this bot.',
        color=discord.Colour.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)

    embed.add_field(
        name='!mod_commands',
        value='List of all the commands exclusively for Moderators.',
        inline=True
    )
    embed.add_field(
        name='!server_info',
        value='Show information about server',
        inline=True
    )
    embed.add_field(
        name='!user info',
        value='Show information about user',
        inline=True
    )
    embed.add_field(
        name='!user_roles',
        value='Show all the roles given to the user',
        inline=True
    )
    embed.add_field(
        name='!user_count',
        value='Show current number of users',
        inline=True
    )
    embed.add_field(
        name='!crypto_help',
        value='Access the help section to learn about how to link your account to helper bot and take advantage of crypto integration',
        inline=False
    )

    await ctx.send(embed=embed)



@client.command()
async def server_info(ctx, user:discord.member=None):  # shows server information

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title='Server Information',
        description='This is an educational server for Bot development. Below is the basic information about the server.',
        color=discord.Colour.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.add_field(
        name='Server Name',
        value='Project Server',
        inline=True
    )
    embed.add_field(
        name='Server Privacy',
        value='Private',
        inline=True
    )
    embed.add_field(
        name='Type',
        value='Non-community',
        inline=True
    )
    await ctx.send(embed=embed)


@client.command()
async def user_info(ctx, user:discord.member=None):  # shows user information

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title='User Information',
        description='Below is the basic information about the user.',
        color=discord.Colour.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)

    embed.add_field(
        name='ID:',
        value=user.id,
        inline=True
    )
    embed.add_field(
        name='Name:',
        value=user.display_name,
        inline=True
    )
    embed.add_field(
        name='Created at:',
        value=user.created_at,
        inline=True
    )
    embed.add_field(
        name='Joined at:',
        value=user.joined_at,
        inline=True
        )
    embed.add_field(
        name='Bot?',
        value=user.bot,
        inline=False
    )
    await ctx.send(embed=embed)

@client.command()
async def user_roles(ctx, user:discord.member=None):  # shows user roles and top role

    if user == None:
        user = ctx.author

    rlist = []
    for role in user.roles:
        if role.name != "@everyone":
            rlist.append(role.mention)

    b = ", ".join(rlist)
    embed = discord.Embed(
        title='Roles',
        description=f'Listed Below are all the roles and the Top role assigned to {user}',
        color=discord.Colour.green(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),  # get author name
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)  # footer including author name and profile icon
    embed.add_field(name=f'Roles:({len(rlist)})', value=''.join([b]), inline=True)
    embed.add_field(name='Top Role:', value=user.top_role.mention, inline=True)
    await ctx.send(embed=embed)


@client.command()
async def user_count(ctx, user:discord.member=None):  # shows current user count of server

    if user==None:
        user = ctx.author

    count = ctx.guild.member_count  # get member count of server
    embed = discord.Embed(
        title=f"Current user count",
        description=f"Listed Below are the total current members in {ctx.guild.name}",
        color=discord.Colour.green(),
        timestamp = ctx.message.created_at
    )
    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.add_field(name='Total count',
                    value=count,
                    inline=True
                    )

    await ctx.send(embed=embed)


@client.command()
async def crypto_help(ctx, user:discord.member=None):  # Show commands related to crypto

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title='Crypto',
        description='Welcome to the help section of crypto transaction handler. Use commands below to link your account and create an account or learn about how to register.',
        color=discord.Colour.red(),
        timestamp=ctx.message.created_at
    )

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.add_field(
        name='!register',
        value='Use this command to start your registration process.',
        inline=True
    )
    embed.add_field(
        name='!register_help',
        value='Use this command to learn the full process of registration process.',
        inline=True
    )
    embed.add_field(
        name='!balance',
        value='Use this command to check current balance of linked account. Only for verified users.',
        inline=True
    )
    embed.add_field(
        name='!verify',
        value='Use this command to verify if your registration process is completed and your discord account is successfully linked to the Helper Bot.',
        inline=True
    )
    await ctx.send(embed=embed)


@client.command()
async def register_help(ctx, user:discord.member=None):  # Shows registration process

    if user==None:
        user = ctx.author

    embed = discord.Embed(
        title=f"Registration help",
        description=f"Listed Below is the Step by Step guide on how to register.",
        color=discord.Colour.red(),
        timestamp=ctx.message.created_at
    )
    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.add_field(name='Step 1:',
                    value="Type '!register' in any channel, then followed by that with single space enter your blockchain account number.",
                    inline=False
                    )
    embed.add_field(name='Step 2:',
                    value="Now make sure that the account number you entered is 64 digits long and doesn't contain special characters, be careful in this step as there are no exceptions allowed and the code will be invalidated.",
                    inline=False
                    )
    embed.add_field(name='Step 3:',
                    value="Once the entered number is validated. You will receive a Direct Message(DM) by the Helper Bot. Go to your DM's and find the latest message sent by Helper Bot, then follow the instructions there.",
                    inline=False
                    )
    embed.add_field(name='Step 4:',
                    value="Now your registration process has started and it's time to verify if the account number you entered is really yours. The sent DM contains 'Helper Bot' account number. Make sure to Copy it.",
                    inline=False
                    )
    embed.add_field(name='Step 5:',
                    value="Now from you any digital wallet. Send the amount of coins mentioned in the DM, to the account number that you just copied in Setp 4.",
                    inline=False
                    )
    embed.add_field(name='Step 6:',
                    value="If all the steps were succefully followed, your account should now be created, to check that use '!verify' command.",
                    inline=False
                    )
    await ctx.send(embed=embed)


@client.command()
async def verify(ctx, user:discord.member=None):  # Checks if the blockchain account is verified or not

    if user==None:
        user = ctx.author
    user_id = ctx.message.author.id

    existing_user = USERS.find_one({'_id': user_id})  # Get all the items values from a table as dictionary
    if existing_user:
        existing_user_acc_num = existing_user["account_number"]
        embed = discord.Embed(
            title=f"Verified",
            description=f"Your account number is linked with the Helper Bot under this discord account.",
            color=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=f"User Info - {user}"),
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
        embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
        embed.add_field(name='Linked account Number:',
                        value=existing_user_acc_num,
                        inline=True
                        )

        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"Not Verified",
            description=f"Sorry! No blockchain account is linked to Helper Bot under this discord account. Please make sure to follow the steps described in '!crypto_help' command to succesfuly link your blockchain account to the Helper Bot",
            color=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=f"User Info - {user}"),
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
        embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)


@client.command()
async def balance(ctx, user:discord.member=None):  # shows current balance of the linked account

    if user==None:
        user = ctx.author
    user_id = ctx.message.author.id

    existing_user = USERS.find_one({'_id': user_id})  # Get all the items values from a table as dictionary

    if existing_user:
        existing_user_acc_num = existing_user["account_number"]
        existing_user_acc_bal = existing_user["balance"]
        embed = discord.Embed(
            title=f"Current Balance",
            description=f"Your account currently has a balance of **{existing_user_acc_bal}** Ether.",
            color=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=f"User Info - {user}"),
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
        embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
        embed.add_field(name='Current account Number:',
                        value=existing_user_acc_num,
                        inline=True
                        )

        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"Error!",
            description=f"Sorry! No blockchain account is linked to Helper Bot under this discord account. To check balance you must link your block chain account with Helper Bot. To learn about how to link, use '!crypto_help' command.",
            color=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=f"User Info - {user}"),
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/950257980333490256/960050435597676544/0c675a8e1061478d2b7b21b330093444.gif'),
        embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
# CUSTOM COMMANDS/HELP AND EMBEDS I.E., Making custom commands,help commands etc. -> END

# Crypto Integration I.E., Registration and validation etc. -> STARTING

@client.command()
async def register(ctx, account_number):  # validation of account number
    """
    !register 4155ca9ce6133b1cbce6623bd10575851cc6780ebf2464f4ca29a5858889f4c3
    """
    str_var = str(account_number)
    eth_acc_num = str_var.lower()
    if not is_valid_account_number(eth_acc_num):  # send back error message
        await send_embed(
            ctx=ctx,
            title="invalid",
            description="Invalid account number"
        )
        return

    user = USERS.find_one({'account_number': eth_acc_num})  # filter for finding out if an account number exists

    if user:  # already registered
        await send_embed(
            ctx=ctx,
            title='Already Registered',
            description=f'The account {eth_acc_num} is already registered.'

        )
        return

    discord_user_id = ctx.author.id

    results = REGISTRATIONS.update_one(  # create or update the existing user registration
        {'_id': discord_user_id},
        {
            '$set': {
                'account_number': eth_acc_num
            }
        },
        upsert=True  # if you can't find account then create new registration, upsert is a combination of update and insert (update + insert = upsert)
    )

    if results.modified_count:
        await send_embed(
            ctx=ctx,
            title='Registration Updated.',
            description=(
                'Your registration has been updated. '
                'To complete registration, follow the instruction sent via DM.'
            )

        )
    else:
        await send_embed(
            ctx=ctx,
            title='Registration Created.',
            description=(
                'Your registration created. '
                'To complete the registration process, follow the instruction sent via DM.'
            )
        )
    await send_verification_message(
        ctx=ctx,
        registration_account_number=account_number
    )  # send verification message




# Crypto Integration I.E., Validation etc. -> END

# Crypto Integration I.E., Registration Logic etc. -> STARTING

"""
REGISTRATION
    _id: 702004040669855825
    account_number: 4155ca9ce6133b1cbce6623bd10575851cc6780ebf2464f4ca29a5858889f4c3
    verification code: 
"""


'''
@client.event
# async def on_profanities(message, word):
#  channel = client.get_channel(980718921533493299)
# embed = discord.Embed(title="Profanity Alert!",description=f"{message.author.name} just said ||{word}||", color=discord.Color.blurple())
# await channel.send(embed=embed)
'''


"""my_secret = os.environ['ton']
client.run('my_secret')"""
# my_secret = os.environ['ton']

# keep_alive()
secret = os.environ.get('my_secret')
client.run(secret)
