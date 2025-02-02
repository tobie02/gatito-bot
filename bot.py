import discord
from discord.ext import commands
from openai import OpenAI
from datetime import datetime
import asyncio

from general import General
from music import Music
from config import *
from supporting.colores import Colores

class GatitoBot(commands.Bot):
    def __init__(self, ai=False):
        super().__init__(
            command_prefix='!',
            activity=discord.Activity(type=discord.ActivityType.listening, name=f"!info or @Tobie"),
            intents=discord.Intents.all(),
        )
        self.intents.message_content = True
        self.ai = ai
        self.contexto_canales = {}
        
        with open('context.txt', 'r', encoding='utf-8') as file:
            self.contexto_inicial = [{"role": "system", "content": file.read()}]

bot = GatitoBot(ai=AI)
interactions = discord.interactions
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

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

# AI Assistant (llama 3.1)
@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return

    # Verificar si el bot fue mencionado directamente (sin contar @everyone o @here)
    if bot.user.mentioned_in(message) and not (message.mention_everyone):
        if bot.ai is False:
            await message.channel.send('Estoy durmiendo, intentalo más tarde 😴')
            return

        if message.channel.id not in bot.contexto_canales:
            bot.contexto_canales[message.channel.id] = bot.contexto_inicial.copy()

        pregunta = message.content.replace(f'<@{bot.user.id}>', '').strip()

        bot.contexto_canales[message.channel.id].append({"role": "user", "content": f'{message.author.name}: {pregunta}'})

        async with message.channel.typing():
            try:
                completion = client.chat.completions.create(
                    model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
                    messages=bot.contexto_canales[message.channel.id],
                    temperature=0.6,
                )
            except:
                await message.channel.send('Estoy durmiendo, intentalo más tarde 😴')
                return
        
        respuesta = completion.choices[0].message.content

        bot.contexto_canales[message.channel.id].append({"role": "assistant", "content": respuesta})

        await message.channel.send(respuesta)
        return

    # Procesar otros comandos del bot
    await bot.process_commands(message)


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
    if before.channel is not None:
        voice = discord.utils.get(bot.voice_clients, channel__guild__id=before.channel.guild.id)
        if voice is None:
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
