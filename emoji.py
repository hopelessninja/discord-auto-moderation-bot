import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  # member intents

client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')


@client.event
async def on_raw_reaction_add(payload):

    target_message_id = 959720999962689598
    if payload.message_id != target_message_id:
        return

    guild = client.get_guild(payload.guild_id)
    print(payload.emoji.name)

client.run('OTA4OTk3OTU0MDU1MDU3NDY5.YY94UA.an5glfrXImVkc4T669MKypg82Wo')