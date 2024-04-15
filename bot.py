import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import asyncio
import requests
import os
from pytube import YouTube, Playlist
from youtube_search import YoutubeSearch

from data import *

intents = discord.Intents.default()
intents.message_content = True

class GatitoBot(commands.Bot):
    def __init__(self):
        super().__init__(
        command_prefix = '!',
        activity = discord.Activity(type=discord.ActivityType.listening, name="!info or @Tobie"),
        intents = discord.Intents.all()
    )
        
bot = GatitoBot()
bot.intents.message_content = True
interactions = discord.interactions
queue = []
results = []
info_descripcion = """
Soy un bot desarrollado en python por @tobie y mi misión es aportar comodidad y control a los usuarios!
Actualmente estoy en BETA por lo que cualquier feedback es bienvenido!
Estos son algunos de mis comandos:
"""
info_general = """
!info - Despliega este cartel
!cat - Muestra un gato random
!dog - Muestra un perro random
!say - Decir algo por en canal de voz
!join - Entrar al canal de voz
!leave - Salir del canal de voz
!vote - Proporner una votación
"""
info_musica = """
!play - Reproducir una canción en el canal de voz
!skip - Saltear canción actual de la playlist
!stop - Termina con la playlist
!pause - Pausa la canción
!resume - Reanuda la canción
!playlist - Muestra la playlist actual
"""


@bot.event
async def on_ready():
    print(f'Gatito bot is ready with discord {discord.__version__}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Test succesfull!', ephemeral=True)

@bot.tree.command(name="w")
async def w(interaction: discord.Interaction, query: str):
    await interaction.response.send_message(f'{interaction.user.name} said: {query}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} entró al servidor.')

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'{member.mention} se fué del servidor.')

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="Gatito Bot",
        description=info_descripcion,
        color=discord.Color.yellow()
    )
    embed.add_field(name="General", value=info_general, inline=False)
    embed.add_field(name="Música", value=info_musica, inline=True)
    embed.set_footer(text="Aurora Software")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/808020134009897051/1228928657704353873/300566938_376828111300945_5460594727833122005_n.jpg?ex=662dd400&is=661b5f00&hm=cdaa36a6f4b7d672746ba6da260f333dbce6bcc13bfa3ba71e1590deaae5538d&")
    embed.set_image(url="https://cdn.discordapp.com/attachments/808020134009897051/1228940730215698522/unnamed.gif?ex=662ddf3e&is=661b6a3e&hm=8b85127394e632a5a8a7bc045fe202053e521a34c6a3b3eb75035c0dc6aca50b&")

    await ctx.send(embed=embed)

@bot.command(help='Muestra un meme de gato')
async def cat(ctx):
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    data = response.json()
    cat_url = data[0]['url']
    await ctx.send(cat_url)

@bot.command(help='Muestra un meme de perro')
async def dog(ctx):
    response = requests.get('https://random.dog/woof.json')
    data = response.json()
    dog_url = data['url']
    await ctx.send(dog_url)

@bot.command(hidden=True, aliases=['w'])
async def write(ctx, *, arg):
    member = ctx.message.author
    await ctx.message.delete()
    print(f"{member.name} asked to '{ctx.message.content}'")
    if ctx.message.channel.name == "console":
        channel = discord.utils.get(member.guild.channels, name="general")
        await channel.send(arg)
    else:
        await ctx.channel.send(arg)

@bot.command(help='Decir algo por canal de voz')
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

    #try:
    source = discord.FFmpegPCMAudio(source)
    ctx.guild.voice_client.play(source)
    #except:
        #await ctx.send('Espera, estoy cantando')

@bot.command(help='Entrar al canal de voz')
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(help='Salir del canal de voz')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        await stop(ctx)
        await voice.disconnect()
    except:
        await ctx.send("No estoy en un canal de voz.")

@bot.command(help="Realiza una votacion")                           
async def vote(ctx, *, message):
    emb = discord.Embed(title=" VOTACION", description=f"{message}")
    msg = await ctx.channel.send(embed=emb)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

def translate_to_spanish(text):
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q=" + text
    response = requests.get(url)
    if response.status_code == 200:
        translated_text = response.json()[0][0][0]
        return translated_text
    else:
        return "Error al traducir el texto."


# MUSICA

@bot.command(aliases=['p'], help='Reproducir musica en el canal de voz')
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return
    else:
        channel = ctx.author.voice.channel

    if not ctx.guild.voice_client:
        await channel.connect()
    else:
        await ctx.guild.voice_client.move_to(channel)

    if query in ['1','2','3','4','5']:
        yt = "https://www.youtube.com/watch?v="
        await add_to_queue(ctx, yt + results[int(query)-1])
    elif 'youtube.com/playlist' in query:
        playlist = Playlist(query)
        for video_url in playlist.video_urls:
            queue.append(video_url)
        await ctx.send(f"🎶 Se han añadido **{len(playlist)}** canciones a la playlist")
        await play_song(ctx)
    elif 'youtube.com' in query:
        await add_to_queue(ctx, query)
    else:
        await search(ctx, query)

async def search(ctx, query: str):
    global results
    results = YoutubeSearch(query, max_results=10).to_dict()
    results = [result['url_suffix'] for result in results]
    yt = "https://www.youtube.com"
    search1 = yt + results[0]
    search2 = yt + results[1]
    search3 = yt + results[2]
    search4 = yt + results[3]
    search5 = yt + results[4]
    searches = f"1. 🎶 {YouTube(search1).author} - {YouTube(search1).title}\n2. 🎶 {YouTube(search2).author} - {YouTube(search2).title}\n3. 🎶 {YouTube(search3).author} - {YouTube(search3).title}\n4. 🎶 {YouTube(search4).author} - {YouTube(search4).title}\n5. 🎶 {YouTube(search5).author} - {YouTube(search5).title}\n"
    await ctx.send(searches)

async def add_to_queue(ctx, url):
    queue.append(url)
    await ctx.send(f"🎶 Se ha añadido **{YouTube(url).title}** a la playlist 🔊")

    if len(queue) == 1:
        await play_song(ctx)

async def play_song(ctx):
    url = queue[0]
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        output_path = stream.download()
        _, file = os.path.split(output_path)
        file = file[:-4]

        try: os.remove('temp.mp3')
        except: pass
        os.rename(output_path, "temp.mp3")

    except Exception as e:
        print(e)
        await ctx.send('El video es demasiado largo y Discord no me permite reproducirlo :(')
        queue.pop(0)

    await ctx.send(f"🎶 Reproduciendo **{file}** en **{ctx.author.voice.channel.name}** 🔊")
    source = discord.FFmpegPCMAudio(source="temp.mp3")
    ctx.guild.voice_client.play(source, after=lambda e: print('terminado', e))
    while ctx.guild.voice_client.is_playing():
        await asyncio.sleep(1)
    queue.pop(0)
    if len(queue) > 0:
        await play_song(ctx)

@bot.command(help='Saltear cancion actual de la playlist')
async def skip(ctx):
    if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.stop()
        await ctx.send("⏭️ Canción omitida. Reproduciendo la siguiente en la cola.")
    else:
        await ctx.send("No se está reproduciendo ninguna canción en este momento.")

@bot.command(help='Mostrar la playlist actual')
async def playlist(ctx):
    if len(queue) == 0:
        await ctx.send("La cola de reproducción está vacía.")
    else:
        try:
            queue_list = "\n".join([f"{index + 1}. {YouTube(url).title}" for index, url in enumerate(queue)])
            await ctx.send(f"**Cola de reproducción:**\n{queue_list}")
        except:
            await ctx.send(f'La playlist es demasiado larga y no entra en un mensaje x.x')

@bot.command(help='Terminar la playlist')
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    global queue
    queue = []
    voice.stop()
    await ctx.send('Terminando la reproduccion de la playlist.')

@bot.command(help='Pausar la musica')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        voice.pause()
        await ctx.send('Pausando música ⏸️')
    except:
        await ctx.send("No estoy reproduciendo nada.")

@bot.command(help='Reanuda la musica')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        voice.resume()
        await ctx.send('Reanudando música ▶️')
    except:
        await ctx.send("No hay una cancion en pausa.")


# SLASH TESTING




if __name__ == '__main__':
    bot.run(TOKEN)