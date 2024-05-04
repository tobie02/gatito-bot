import discord
from discord.ext import commands
from datetime import datetime
import asyncio

from general import General
from music import Music
from config import *
from supporting.colores import Colores

class GatitoBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix = '!',
        activity = discord.Activity(type=discord.ActivityType.listening, name=f"!info or @Tobie"),
        intents = discord.Intents.all(),
    )
        
bot = GatitoBot()
bot.intents.message_content = True
interactions = discord.interactions

@bot.event
async def on_ready():

    print(f'{Colores.NEGRO}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {INFO}{Colores.AZUL}{Colores.NEGRITA}Gatito bot {Colores.RESET}is ready with {Colores.MAGENTA}discord {discord.__version__}')

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

GUILD_VC_TIMER = {}
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return
    if before.channel != None:
        voice = discord.utils.get(bot.voice_clients , channel__guild__id = before.channel.guild.id) 
        if voice == None:
            return
        if voice.channel.id != before.channel.id:
            return
        if len(voice.channel.members) <= 1:
            GUILD_VC_TIMER[before.channel.guild.id] = 0
            while True:
                print(f'{Colores.NEGRO}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Colores.RESET} {INFO}{Colores.AMARILLO}Time {str(GUILD_VC_TIMER[before.channel.guild.id])} {Colores.RESET}Total Members: {Colores.ROJO}{str(len(voice.channel.members))}')
                await asyncio.sleep(1)
                GUILD_VC_TIMER[before.channel.guild.id] += 1
                if len(voice.channel.members) >= 2 or not voice.is_connected():
                    break
                if GUILD_VC_TIMER[before.channel.guild.id] >= 5:
                    await voice.disconnect()
                    return


bot.run(TOKEN)