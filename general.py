import discord
from discord.ext import commands
from gtts import gTTS
import requests

class General(commands.Cog, name='General'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Muestra la info del bot')
    async def info(self, ctx):
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
        !vote - Proporner una votación
        """
        info_musica = """
        !play - Reproducir una canción en el canal de voz
        !skip - Saltear canción actual de la playlist
        !stop - Termina con la playlist
        !pause - Pausa la canción
        !resume - Reanuda la canción
        !join - Entrar al canal de voz
        !leave - Salir del canal de voz
        !playlist - Muestra la playlist actual
        """
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

    @commands.command(help='Muestra un meme de gato')
    async def cat(self, ctx):
        response = requests.get('https://api.thecatapi.com/v1/images/search')
        data = response.json()
        cat_url = data[0]['url']
        await ctx.send(cat_url)

    @commands.command(help='Muestra un meme de perro')
    async def dog(self, ctx):
        response = requests.get('https://random.dog/woof.json')
        data = response.json()
        dog_url = data['url']
        await ctx.send(dog_url)

    @commands.command(hidden=True, aliases=['w'])
    async def write(self, ctx, *, arg):
        member = ctx.message.author
        await ctx.message.delete()
        print(f"{member.name} asked to '{ctx.message.content}'")
        if ctx.message.channel.name == "console":
            channel = discord.utils.get(member.guild.channels, name="general")
            await channel.send(arg)
        else:
            await ctx.channel.send(arg)

    @commands.command(help='Decir algo por canal de voz')
    async def say(self, ctx, *, arg):
        if not ctx.author.voice:
            await ctx.send("Debes estar en un canal de voz para usar este comando.")
            return
        else:
            channel = ctx.author.voice.channel

        if not ctx.guild.voice_client:
            await channel.connect()
        else:
            await ctx.guild.voice_client.move_to(channel)

        source = 'temp/speech.mp3'
        language = 'es'
        sp = gTTS(text = arg, lang = language, slow = False)
        sp.save(source)

        try:
            source = discord.FFmpegPCMAudio(source)
            ctx.guild.voice_client.play(source)
        except:
            await ctx.send('Espera, estoy cantando')

    @commands.command(help="Realiza una votacion")                           
    async def vote(self, ctx, *, message):
        emb = discord.Embed(title=" VOTACION", description=f"{message}")
        msg = await ctx.channel.send(embed=emb)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

    def translate_to_spanish(self, text):
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q=" + text
        response = requests.get(url)
        if response.status_code == 200:
            translated_text = response.json()[0][0][0]
            return translated_text
        else:
            return "Error al traducir el texto."
        

    @commands.command(hidden=True, aliases=['muteall', 'm'])                     # MUTE ALL
    async def vcmute(self, ctx):
        if ctx.message.author.id == 209879067879669760:
            vc = ctx.author.voice.channel
            for member in vc.members:
                await member.edit(mute=True)
        else:
            await ctx.channel.send("Solo mi creador Tobi puede usar ese comando")


    @commands.command(hidden=True, aliases=['unmuteall', 'um'])                       # UNMUTE ALL
    async def vcunmute(self, ctx):
        if ctx.message.author.id == 209879067879669760:
            vc = ctx.author.voice.channel
            for member in vc.members:
                await member.edit(mute=False)
        else:
            await ctx.channel.send("Solo mi creador Tobi puede usar ese comando")
   