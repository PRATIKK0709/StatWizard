# main.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.webhooks = True
intents.guilds = True
bot = commands.Bot(command_prefix='.', intents=intents)

async def load_cogs():
    cogs_loaded = []
    cogs_failed = []

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(cog_name)
                cogs_loaded.append(cog_name)
            except Exception as e:
                cogs_failed.append((cog_name, str(e)))

    print("Cogs loaded successfully:")
    for cog in cogs_loaded:
        print(f"- {cog}")

    if cogs_failed:
        print("Cogs failed to load:")
        for cog, error in cogs_failed:
            print(f"- {cog}: {error}")

@bot.event
async def on_ready(): 
    await load_cogs()
    print(f'{bot.user} has connected to Discord!')

bot.run(os.getenv('DISCORD_TOKEN'))
