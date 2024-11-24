import discord
from discord.ext import commands
from dotenv import load_dotenv
import os 
import asyncio

# Bot configuration
import logging

# logging.basicConfig(level=logging.DEBUG)  For debug
load_dotenv()
TOKEN = os.getenv("TOKEN") 
PREFIX = "!"  
guild_id = ["1162672034262814728","1181528878993395712"]
# Set up the bot with a command prefix
intents = discord.Intents.default()  # Set up intents (default permissions)
intents.messages = True  # Allow the bot to read messages
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# FFmpeg options for audio streaming
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

@bot.event
async def on_command(ctx):
    user = ctx.author
    command = ctx.command.name
    guild = ctx.guild.name if ctx.guild else "DM"
    
    # Log information
    logging.info(f"User: {user} (ID: {user.id}) used command: {command} in: {guild}")
    print(f"Logged: {user} used {command} in {guild}")


# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")
    
# Command: Ping


# Command: Say
@bot.slash_command(name="hello", description="Say hello", guild_ids = guild_id)
async def hello(ctx):
    await ctx.respond("Hello, world!")
# Run the bot

async def load_extensions():
    try:
        await bot.load_extension("cogs.base")
        print("Successfully loaded cogs.base!")
    except Exception as e:
        print(f"Failed to load cogs.base: {e}")
bot.load_extension("cogs.music")
bot.load_extension("cogs.base")
bot.run(TOKEN)
