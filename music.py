import discord
from discord.ext import commands

import os
import asyncio
from pytube import YouTube, Playlist
from youtube_search import YoutubeSearch

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
        self.queue.append(url)
        await ctx.send(f"🎶 Se ha añadido **{YouTube(url).title}** a la playlist 🔊")

        if len(self.queue) == 1:
            await self.play_song(ctx)

    async def play_song(self, ctx):
        url = self.queue[0]
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            output_path = stream.download()
            _, file = os.path.split(output_path)
            file = file[:-4]

            try: os.remove('temp/song.mp3')
            except: pass
            os.rename(output_path, "temp/song.mp3")

        except Exception as e:
            print(e)
            await ctx.send('El video es demasiado largo o tiene restricción de edad')
            self.queue.pop(0)

        await ctx.send(f"🎶 Reproduciendo **{file}** en **{ctx.author.voice.channel.name}** 🔊")
        source = discord.FFmpegPCMAudio(source="temp/song.mp3")
        ctx.guild.voice_client.play(source, after=lambda e: print('terminado', e))
        while ctx.guild.voice_client.is_playing():
            await asyncio.sleep(1)
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

