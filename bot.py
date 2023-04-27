import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import Button, ButtonStyle
from discord import FFmpegPCMAudio
from data import *

from urllib import parse, request
from gtts import gTTS
import youtube_dl
import os
import re


intents = discord.Intents.default()
intents.message_content = True


class GatitoBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix = '!',
        activity = discord.Activity(type=discord.ActivityType.listening, name="/help or @Tobie#0002"),
        intents = discord.Intents.all()
    )
        
bot = GatitoBot()
interactions = discord.interactions

class SimpleView(discord.ui.View):

    @discord.ui.button(label="Hello", style=discord.ButtonStyle.primary)
    async def hello(self, interaction, button):
        await interaction.response.send_message('Clicked!')


@bot.command()
async def button(ctx):
    view = discord.ui.View()
    button1 = discord.ui.Button(label='1', style=discord.ButtonStyle.primary)
    button2 = discord.ui.Button(label='2', style=discord.ButtonStyle.primary)
    button3 = discord.ui.Button(label='3', style=discord.ButtonStyle.primary)
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)
    await ctx.send(view=view)


@bot.event
async def on_ready():
    print(f'Gatito bot is ready with discord {discord.__version__}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} entró al servidor.')

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} se fué del servidor.')

@bot.command()
async def w(ctx, *, arg):
    member = ctx.message.author
    await ctx.message.delete()
    print(f"{member.name} asked to '{ctx.message.content}'")
    if ctx.message.channel.name == "console":
        channel = discord.utils.get(member.guild.channels, name="general")
        await channel.send(arg)
    else:
        await ctx.channel.send(arg)

@bot.command()
async def say(ctx, *, arg):
    if not ctx.author.voice:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return
    else:
        channel = ctx.author.voice.channel

    if not ctx.guild.voice_client:
        await channel.connect()
    else:
        await ctx.guild.voice_client.move_to(channel)

    source = 'files/speech.mp3'
    language = 'es'
    sp = gTTS(text = arg, lang = language, slow = False)
    sp.save(source)

    try:
        source = FFmpegPCMAudio(source)
        ctx.guild.voice_client.play(source)
    except:
        await ctx.send('Espera, estoy cantando')

@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return
    else:
        channel = ctx.author.voice.channel

    if not ctx.guild.voice_client:
        await channel.connect()
    else:
        await ctx.guild.voice_client.move_to(channel)

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except:
        await ctx.send(f"Ya se esta reproduciendo música, espera que termine la cancion actual o utiliza el comando !stop")
        return

    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            garbage = url.split('watch?v=')[-1]
            name = file.replace(f'-{garbage}', '').replace('.mp3', '')
            os.rename(file, "song.mp3")

    await ctx.send(f"🎶 Reproduciendo **{name}** en **{channel.name}** 🔊")

    source = "song.mp3"
    source = FFmpegPCMAudio(source)
    ctx.guild.voice_client.play(source)

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send('Cortando la reproduccion de la canción.')

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        voice.pause()
        await ctx.send('Pausando música 🎶')
    except:
        await ctx.send("No estoy reproduciendo nada.")

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        voice.resume()
        await ctx.send('Reanudando música 🎶')
    except:
        await ctx.send("No hay una cancion en pausa.")

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        await voice.disconnect()
    except:
        await ctx.send("No estoy en un canal de voz.")
    
@bot.command()
async def search(ctx, *, search: str):
    
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.findall( r"watch\?v=(\S{11})", html_content.read().decode())
    print(search_results)
    yt = "https://www.youtube.com/watch?v="
    search1 = yt + search_results[0]
    search2 = yt + search_results[1]
    search3 = yt + search_results[2]
    search4 = yt + search_results[3]
    search5 = yt + search_results[4]
    await ctx.send("1. " + search1)
    await ctx.send("2. " + search2)
    await ctx.send("3. " + search3)
    await ctx.send("4. " + search4)
    await ctx.send("5. " + search5)
    return



if __name__ == '__main__':
    bot.run(TOKEN)