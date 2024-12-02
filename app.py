import discord
from discord.ext import commands
from dotenv import load_dotenv
import os 

from api.botevent import BotEvent
import logging

# logging.basicConfig(level=logging.DEBUG)  For debug
load_dotenv()
TOKEN = os.getenv("TOKEN") 
PREFIX = "!"  
guild_id = ["1162672034262814728","1181528878993395712"]
# Set up the bot with a command prefix
intents = discord.Intents.default()  # Set up intents (default permissions)
intents.messages = True  # Allow the bot to read messages
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)



@bot.event
async def on_command(ctx):
    user = ctx.author
    command = ctx.command.name
    guild = ctx.guild.name if ctx.guild else "DM"   
    # Log information
    logging.info(f"User: {user} (ID: {user.id}) used command: {command} in: {guild}")
    print(f"Logged: {user} used {command} in {guild}")
@bot.listen()
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if "<@1309145643629150218>" in message.content:
        await BotEvent(msg = message,bot=bot,user_id = message.author.id,user_name = message.author.name).OpenaiApi()
    # await message.reply(message)


@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")
    
@bot.slash_command(name="test", description="test",guild_ids = guild_id)
async def test(ctx):
    user = await bot.fetch_user(786759023361785867)
    await user.send("Hello there!")
async def load_extensions():
    try:
        await bot.load_extension("cogs.base")
        print("Successfully loaded cogs.base!")
    except Exception as e:
        print(f"Failed to load cogs.base: {e}")
bot.load_extension("cogs.music")
bot.load_extension("cogs.base")
bot.run(TOKEN)
