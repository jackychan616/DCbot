import discord
from discord.ext import commands
from dotenv import load_dotenv
import os 
import asyncio
import yt_dlp as youtube_dl
from urlextract import URLExtract
from youtube_search import YoutubeSearch
from api.openaiapi import OpenAiApi
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
youtube_dl.utils.bug_reports_message = lambda: ""

# FFmpeg options for audio streaming
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

extractor = URLExtract()

@bot.slash_command(name="join", description="Join the voice channel",guild_ids = guild_id)
async def join(ctx: discord.ApplicationContext):
    if not ctx.author.voice:
        await ctx.respond("You need to be in a voice channel for me to join!")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()
    await ctx.respond("Joined the voice channel!")

@bot.slash_command(name="leave", description="Leave the voice channel",guild_ids = guild_id)
async def leave(ctx: discord.ApplicationContext):
    if not ctx.author.voice:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.respond("Left the voice channel!")
        else:
            await ctx.respond("I'm not connected to any voice channel.")
    else:
        await ctx.respond("fuck you join chat to kick me")

playlist = {}
async def getSong(ctx,song):
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(song, download=False)
                url2 = info['url']
                title = info.get('title', 'Unknown Title')
            except Exception as e:
                await ctx.respond(e)
                return
        return {"url":url2,"title":title}
async def playSong(ctx,url,title,vc):
        data = await getSong(ctx,url)
        url = data["url"]
        title = data["title"]
        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: next_song(ctx))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.5
        await ctx.respond(f"Now playing: {title}")
def next_song(ctx):
    guild_id = ctx.guild.id
    if guild_id in playlist and playlist[guild_id]:
        next_url,next_title = playlist[guild_id].pop(0)
        vc = ctx.voice_client
        bot.loop.create_task(playSong(ctx=ctx, vc=vc, url=next_url, title=next_title))


async def SearchSongWithList(songlist):
        songlist_url = []
        for song in songlist:
            url = YoutubeSearch(song,max_results=10).to_dict()
            url = "https://www.youtube.com/" + url[0]["url_suffix"]
            songlist_url.append(url)
        return songlist_url
@bot.slash_command(name="autoplay",description="auto play",guild_ids=guild_id)
async def autoplay(ctx , 
    lang = discord.Option(
        input_type="str",
        default = "中文",
        required = True,
        description="Choose Lang",
        choices=["中文","粵語","英語","日語","混合"]
        ),
    style = discord.Option(
        input_type = "str",
        default = "pop",
        required = True,
        description= "Choose songs style",
        choices = ["Pop ","Rock","Hip-Hop/Rap","R&B","Classical","no require"]
    ),
    artist = discord.Option(
        description="你可以選擇不選歌手",
        required = False,
        default = "None"
        ),
    requ = discord.Option(
        input_type = "str",
        description= "what you want",
        default = ""
    )
    ):
    if not ctx.author.voice:
        await ctx.respond("You need to be in a voice channel for me to join!")
        return
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
    await ctx.defer()
    guild = ctx.guild.id
    if guild  not in playlist:
        playlist[guild] = []
    res = await OpenAiApi(Lang = lang , style = style,req = requ).getRes()
    embed = discord.Embed(
        title = "Auto playlist",
        description= lang
    )
    embed.add_field(name="",value=f"**{style if style != None or style != "" else "No choosen style"}**",inline=False)
    songlist = []
    
    for key in list(res[0]):
        embed.add_field(name=key,value="",inline=True)
    for i in res:
        songlist.append(i["title"])
        embed.add_field(name="",
                            value=i["title"],
                            inline=False
        )
    songlist_url = await SearchSongWithList(songlist=songlist)
    for i in range(len(songlist)):
         playlist[guild].append((songlist_url[i], songlist[i]))
    await ctx.respond(embed = embed)
    vc = ctx.voice_client
    if not vc.is_playing():
        url,title = playlist[guild].pop(0)
        await playSong(ctx=ctx,url = url,title = title ,vc=vc)
@bot.slash_command(name="test",description="test",guild_ids=guild_id)
async def test(ctx):
    await ctx.respond(playlist)
            
        

    

@bot.slash_command(name="play", description="Play a song from a YouTube URL",guild_ids = guild_id)
async def play(ctx: discord.ApplicationContext, url: str):
    guild = ctx.guild.id
    if guild not in playlist:
        playlist[guild] = []
    await ctx.defer()
    if not ctx.voice_client:
        await ctx.respond("I need to be in a voice channel to play music! Use /join first.")
        return
    if extractor.has_urls(url):
        url = extractor.find_urls[0]
    else:
        url = YoutubeSearch(url,max_results=10).to_dict()
        url = "https://www.youtube.com/" + url[0]["url_suffix"]
    vc = ctx.voice_client
    if not vc.is_playing():
        await playSong(ctx=ctx,url = url,vc=vc)
    else:
        data = await getSong(ctx,url)
        playlist[guild].append((url,data["title"]))
        await ctx.respond(f"Added to the queue : {data["title"]}")
@bot.slash_command(name="queue", description= "playlist of guild",guild_ids = guild_id)
async def queue(ctx):
    guild = ctx.guild.id
    res = ""
    if guild in playlist and playlist[guild] != []:
        for i in playlist[guild]:
            res += i[1] + "\n" 
        await ctx.respond(res)
    else:
        await ctx.respond("Nothing in queue ! Please use `/play <song>` add some song")
@bot.slash_command(name="skip",description="skip the current music")
async def skip(ctx: discord.ApplicationContext):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.respond("Skipped")
    else:
        await ctx.respond("NO song Or you are not in vc")
@bot.slash_command(name="pause", description="Pause the current song")
async def pause(ctx: discord.ApplicationContext):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.respond("Paused the music!")
    else:
        await ctx.respond("There's no music playing to pause.")

@bot.slash_command(name="resume", description="Resume the current song")
async def resume(ctx: discord.ApplicationContext):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.respond("Resumed the music!")
    else:
        await ctx.respond("There's no music paused to resume.")

@bot.slash_command(name="stop", description="Stop the music")
async def stop(ctx: discord.ApplicationContext):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        playlist[ctx.guild.id] = [] # clear the queue of the guild
        await ctx.respond("Stopped the music!")
    else:
        await ctx.respond("There's no music playing to stop.")

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

bot.run(TOKEN)
