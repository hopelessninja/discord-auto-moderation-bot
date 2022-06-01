import string

import discord
import random
from config.settings import BOT_ACCOUNT_NUMBER


async def send_embed(*, ctx, title, description):
    """

    Send a simple embed with a title and description
    """
    user: discord.member = None

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Colour.red(),
        timestamp=ctx.message.created_at
    )
    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(
        url='https://media.discordapp.net/attachments/980719071739920394/981573917187657749/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

async def roles_send_embed(*, payload, channel, username, title, description):
    """

    Send a simple embed with a title and description
    """
    user: discord.member = None

    if user == None:
        #user = client.get_user(payload.user_id)
        user = payload.user_id

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Colour.red(),
    )
    embed.set_author(name=f"User Info - {username}"),
    embed.set_thumbnail(
        url='https://media.discordapp.net/attachments/980719071739920394/981573917187657749/0c675a8e1061478d2b7b21b330093444.gif')
    # await guild.get_channel(payload.channel_id).send("I couldn't find that role...")
    await channel.send(embed=embed)

async def send_verification_message(*, ctx, registration_account_number):  # Send verification message DM

    user: discord.member = None
    value = 0.0001

    if user == None:
        user = ctx.author

    embed = discord.Embed(
        title='Account Registration',
        description= 'To complete the registration please send the following transaction.',
        color=discord.Colour.red(),
        timestamp=ctx.message.created_at
    )
    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(
        url='https://media.discordapp.net/attachments/980719071739920394/981573917187657749/0c675a8e1061478d2b7b21b330093444.gif'),
    embed.set_footer(text=f'Requested by - {ctx.author}', icon_url=ctx.author.avatar_url)
    embed.add_field(
        name='From',
        value=registration_account_number,
        inline=False
    )
    embed.add_field(
        name='To',
        value=BOT_ACCOUNT_NUMBER,
        inline=False
    )
    embed.add_field(
        name='Amount',
        value=str(value),
        inline=False
    )

    await ctx.author.send(embed=embed)