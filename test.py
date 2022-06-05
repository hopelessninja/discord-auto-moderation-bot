import discord, os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  # member intents

client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')


@client.event
async def on_raw_reaction_add(payload):

    target_message_id = 981859721852100679
    if payload.message_id != target_message_id:
        return

    guild = client.get_guild(payload.guild_id)
    print(payload.emoji.name)


@client.command()
async def send(ctx, user:discord.member=None):  # shows current balance of the linked account

    if user==None:
        user = ctx.author
    user_id = ctx.message.author.id

    """existing_user = USERS.find_one({'_id': user_id})  # Get all the items values from a table as dictionary

    if existing_user:
        existing_user_acc_num = existing_user["account_number"]
        existing_user_acc_bal = existing_user["balance"]"""

    embed = discord.Embed(
        title=f"Buy Games",
        description=f"To buy Game keys to redeem your favorite game, please react with appropriate emoji(s) below:",
        color=discord.Colour.blurple(),
        timestamp=ctx.message.created_at
    )
    embed.set_thumbnail(
        url='https://media.discordapp.net/attachments/980719071739920394/981573917187657749/0c675a8e1061478d2b7b21b330093444.gif')

    embed.add_field(name='Grand Theft Auto V',
                    value="<:gtav:981862365207363645>  |  `1 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Red Dead Redemption 2',
                    value="<:rdr2:981862366008463402>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Battlefield 2042',
                    value="<:bf42:981862364943101952>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Forza Horizon 4',
                    value="<:fh4:981862364158787605>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Call of Duty: Modern Warfare',
                    value="<:mw:981862363873562624>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Call of Duty: Vanguard',
                    value="<:vanguard:981862537748426762>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Microsoft Flight Simulator 2020',
                    value="<:msfs2020:981862368013336576>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )
    embed.add_field(name='Halo Infinite',
                    value="<:halo_infinite:981862364846641152>  |  `3 key(s) left`  |  `0.0170 ethers per item`",
                    inline=False
                    )

    msg = await ctx.send(embed=embed)
    await msg.add_reaction('<:gtav:981862365207363645>')
    await msg.add_reaction('<:rdr2:981862366008463402>')
    await msg.add_reaction('<:bf42:981862364943101952>')
    await msg.add_reaction('<:fh4:981862364158787605>')
    await msg.add_reaction('<:mw:981862363873562624>')
    await msg.add_reaction('<:vanguard:981862537748426762>')
    await msg.add_reaction('<:msfs2020:981862368013336576>')
    await msg.add_reaction('<:halo_infinite:981862364846641152>')



client.run(os.environ.get('my_secret'))
