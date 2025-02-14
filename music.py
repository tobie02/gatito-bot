import discord
from discord.ext import commands

import os
import asyncio
from pytubefix import YouTube, Playlist
from youtube_search import YoutubeSearch


'''
FFMPEG INSTALL HERE
-------------------
https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/

PYTUBE FIX
----------
cipher.py

line - 30 should be
var_regex = re.compile(r"^[\w\$_]+\W")

line - 264 should be
function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]

LAST ISSUE AUG 8, 2024 SOLUTION:

line 264 should be:
function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]

function at 232 should be:

transform_object = get_transform_object(js, var)
mapper = {}
for obj in transform_object:
    # AJ:function(a){a.reverse()} => AJ, function(a){a.reverse()}
    name, function = obj.split(":", 1)
    if function == '"jspb"':
        continue
    fn = map_functions(function)
    mapper[name] = fn
return mapper


CHECK IF NEW ISSUES HERE: https://github.com/pytube/pytube/issues
'''

class Music(commands.Cog, name='Musica'):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.results = []

    @commands.command(aliases=['p'], help='Reproducir musica en el canal de voz')
    async def play(self, ctx, *, query):
        if ctx.message.channel.name != "musica":
            await ctx.send("Aca no flaco, tenes un canal de música")
            return
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
            await self.add_to_queue(ctx, yt + self.results[int(query)-1])
        elif 'youtube.com/playlist' in query:
            playlist = Playlist(query)
            for video_url in playlist.video_urls:
                self.queue.append(video_url)
            await ctx.send(f"🎶 Se han añadido **{len(playlist)}** canciones a la playlist")
            if not ctx.guild.voice_client.is_playing():
                await self.play_song(ctx)
        elif 'youtube.com' in query:
            await self.add_to_queue(ctx, query)
        else:
            await self.search(ctx, query)

    async def search(self, ctx, query: str):
        self.results = YoutubeSearch(query, max_results=5).to_dict()
        videos = [YouTube("https://www.youtube.com" + result['url_suffix']) for result in self.results]
        self.results = [result['url_suffix'] for result in self.results]
        if len(videos) < 1:
            await ctx.send('No hay resultados con ese input')
        else:
            searches = ''
            n = 1
            for video in videos:
                searches += f'{n}. 🎶 **{video.author}** - {video.title}\n'
                n += 1
            await ctx.send(searches)

    async def add_to_queue(self, ctx, url):
        print((YouTube(url).author.lower() + YouTube(url).title.lower()))
        #if 'anuel' in (YouTube(url).author.lower() + YouTube(url).title.lower()):
        #    await ctx.send(f"🎶 Mi amo no me permite reproducir musica horrible como la de Anuel")
        #    return
        self.queue.append(url)
        await ctx.send(f"🎶 Se ha añadido **{YouTube(url).title}** a la playlist 🔊")

        if len(self.queue) == 1:
            await self.play_song(ctx)

    async def download_song(self, url):
        try: os.remove('temp/song.mp3')
        except: pass
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        output_path = stream.download()
        _, file = os.path.split(output_path)
        self.file = file[:-4]
        os.rename(output_path, "temp/song.mp3")

    async def play_song(self, ctx):
        url = self.queue[0]
        try:
            await self.download_song(url)
        except Exception as e:
            print(e)
            await ctx.send('El video es demasiado largo o tiene restricción de edad')
            self.queue.pop(0)
            return

        await ctx.send(f"🎶 Reproduciendo **{self.file}** en **{ctx.author.voice.channel.name}** 🔊")
        source = discord.FFmpegPCMAudio(source="temp/song.mp3")
        ctx.guild.voice_client.play(source, after=lambda e: print('terminado', e))

        while ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
            await asyncio.sleep(1)

        if not ctx.guild.voice_client:
            print('Disconnected from channel. Stopping queue')
            self.queue = []
        if ctx.guild.voice_client:
            self.queue.pop(0)
            if len(self.queue) > 0:
                await self.play_song(ctx)

    @commands.command(help='Saltear cancion actual de la playlist')
    async def skip(self, ctx):
        if ctx.guild.voice_client and ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            await ctx.send("⏭️ Canción omitida. Reproduciendo la siguiente en la cola.")
        else:
            await ctx.send("No se está reproduciendo ninguna canción en este momento.")

    @commands.command(help='Mostrar la playlist actual')
    async def playlist(self, ctx):
        if len(self.queue) == 0:
            await ctx.send("La cola de reproducción está vacía.")
        else:
            if len(self.queue) > 10:
                await ctx.send("Espera, esto esta re largo...")
            try:
                queue_list = "\n".join([f"{index + 1}. {YouTube(url).title}" for index, url in enumerate(self.queue)])
                await ctx.send(f"**Cola de reproducción:**\n{queue_list}")
            except:
                await ctx.send(f'La playlist es demasiado larga y no entra en un mensaje x.x')

    @commands.command(help='Terminar la playlist')
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        self.queue = []
        voice.stop()
        await ctx.send('Terminando la reproduccion de la playlist.')

    @commands.command(help='Pausar la musica')
    async def pause(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            voice.pause()
            await ctx.send('Pausando música ⏸️')
        except:
            await ctx.send("No estoy reproduciendo nada.")

    @commands.command(help='Reanuda la musica')
    async def resume(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            voice.resume()
            await ctx.send('Reanudando música ▶️')
        except:
            await ctx.send("No hay una cancion en pausa.")

    @commands.command(help='Salir del canal de voz')
    async def leave(self, ctx):
        voice = discord.utils.get(self.voice_clients, guild=ctx.guild)
        try:
            if ctx.guild.voice_client.is_playing():
                await self.stop(ctx)
            await voice.disconnect()
        except:
            await ctx.send("No estoy en un canal de voz.")

    @commands.command(help='Entrar al canal de voz')
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()

