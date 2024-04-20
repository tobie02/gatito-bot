import discord
from discord.ext import commands

from general import General
from music import Music
from config import *

class GatitoBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix = '!',
        activity = discord.Activity(type=discord.ActivityType.listening, name="!info or @Tobie"),
        intents = discord.Intents.all(),
    )
        
bot = GatitoBot()
bot.intents.message_content = True
interactions = discord.interactions

@bot.event
async def on_ready():

    print(f'Gatito bot is ready with discord {discord.__version__}')

    try: await bot.add_cog(General(bot))
    except Exception as e: print(e)

    try: await bot.add_cog(Music(bot))
    except Exception as e: print(e) 

    try: synced = await bot.tree.sync()
    except Exception as e: print(e)

@bot.tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hola **{interaction.user}**, gracias por saludarme!")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} entró al servidor.')

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} se fué del servidor.')


bot.run(TOKEN)