import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from urlextract import URLExtract
from youtube_search import YoutubeSearch
from api.openaiapi import OpenAiApi
from api.gc_tts import TTS
from utils.langcode import getLangCode
from temp.playlist import playlist
guild_id = ["1162672034262814728","1181528878993395712"]       

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
youtube_dl.utils.bug_reports_message = lambda: ""

extractor = URLExtract()    
async def SearchSongWithList(songlist):
        songlist_url = []
        for song in songlist:
            url = YoutubeSearch(song,max_results=10).to_dict()
            url = "https://www.youtube.com/" + url[0]["url_suffix"]
            songlist_url.append(url)
        return songlist_url        
class MusicCmd(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.playlist = playlist
    async def getSong(self,ctx,song):
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(song, download=False)
                url2 = info['url']
                title = info.get('title', 'Unknown Title')
            except Exception as e:
                await ctx.respond(e)
                return
        return {"url":url2,"title":title}
    def next_song(self,ctx):
            guild = ctx.guild.id
            if guild in self.playlist and self.playlist[guild]:
                next_url,next_title = self.playlist[guild].pop(0)
                vc = ctx.voice_client
                self.bot.loop.create_task(self.playSong(ctx=ctx, vc=vc, url=next_url, title=next_title))
    async def NextSongNoti(self,ctx,title):
                lg_c = await getLangCode(title)
                print(lg_c)
                # await TTS(text = title,Lang_code = lg_c).getAudio()
                ctx.voice_client.play(discord.FFmpegPCMAudio("output.mp3"),after = ctx.voice_client.stop())
                return
    async def playSong(self,ctx,url,title,vc):
        data = await self.getSong(ctx,url)
        url = data["url"]
        title = data["title"]
        
        # await self.NextSongNoti(ctx=ctx,title = title)
        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: self.next_song(ctx))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.5
        await ctx.respond(f"Now playing: {title}")
    @discord.slash_command(name="join", description="Join the voice channel",guild_ids = guild_id)
    async def join(self,ctx: discord.ApplicationContext):
        if not ctx.author.voice:
            await ctx.respond("You need to be in a voice channel for me to join!")
            return
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        await ctx.respond("Joined the voice channel!")

    @discord.slash_command(name="leave", description="Leave the voice channel",guild_ids = guild_id)
    async def leave(self,ctx: discord.ApplicationContext):
        if not ctx.author.voice:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
                await ctx.respond("Left the voice channel!")
            else:
                await ctx.respond("I'm not connected to any voice channel.")
        else:
            await ctx.respond("fuck you join chat to kick me")
    @discord.slash_command(name="clear",descriptoin = "Clear the queue",guild_ids = guild_id)
    async def clear(self,ctx):
        if ctx.guild.id in self.playlist: # clear guild playlist
            self.playlist[ctx.guil.id] = []
        await ctx.respond("Your queue is cleared ! ")



    @discord.slash_command(name="autoplay",description="auto play",guild_ids=guild_id)
    async def autoplay(self,ctx , 
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
        if guild  not in self.playlist:
            self.playlist[guild] = []
        res = await OpenAiApi(Lang = lang , style = style,req = requ,artist=artist).getSongList()
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
            self.playlist[guild].append((songlist_url[i], songlist[i]))
        await ctx.respond(embed = embed)
        vc = ctx.voice_client
        if not vc.is_playing():
            url,title = self.playlist[guild].pop(0)
            await self.playSong(ctx=ctx,url = url,title = title ,vc=vc)
            
        

    

    @discord.slash_command(name="play", description="Play a song from a YouTube URL",guild_ids = guild_id)
    async def play(self,ctx: discord.ApplicationContext, url: str):
        guild = ctx.guild.id
        if guild not in self.playlist:
            self.playlist[guild] = []
        await ctx.defer()
        if not ctx.voice_client:
            await ctx.respond("I need to be in a voice channel to play music! Use /join first.")
            return
        try:
            if extractor.has_urls(url):
                url = extractor.find_urls[0]
            else:
                url = YoutubeSearch(url,max_results=10).to_dict()
                url = "https://www.youtube.com/" + url[0]["url_suffix"]
        except Exception as e:
            await ctx.respond(e)
            return
        vc = ctx.voice_client
        if not vc.is_playing():
            data = await self.getSong(ctx,url)
            await self.playSong(ctx=ctx,url = url,title=data["title"],vc=vc)
        else:
            data = await self.getSong(ctx,url)
            self.playlist[guild].append((url,data["title"]))
            await ctx.respond(f"Added to the queue : {data["title"]}")
    @discord.slash_command(name="queue", description= "playlist of guild",guild_ids = guild_id)
    async def queue(self,ctx):
        guild = ctx.guild.id
        res = ""
        if guild in self.playlist and self.playlist[guild] != []:
            for i in self.playlist[guild]:
                res += i[1] + "\n" 
            await ctx.respond(res)
        else:
            await ctx.respond("Nothing in queue ! Please use `/play <song>` add some song")
    @discord.slash_command(name="skip",description="skip the current music")
    async def skip(self,ctx: discord.ApplicationContext):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.respond("Skipped")
        else:
            await ctx.respond("NO song Or you are not in vc")
    @discord.slash_command(name="pause", description="Pause the current song")
    async def pause(self,ctx: discord.ApplicationContext):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.respond("Paused the music!")
        else:
            await ctx.respond("There's no music playing to pause.")

    @discord.slash_command(name="resume", description="Resume the current song")
    async def resume(self,ctx: discord.ApplicationContext):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.respond("Resumed the music!")
        else:
            await ctx.respond("There's no music paused to resume.")

    @discord.slash_command(name="stop", description="Stop the music")
    async def stop(self,ctx: discord.ApplicationContext):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.playlist[ctx.guild.id] = [] # clear the queue of the guild
            await ctx.respond("Stopped the music!")
        else:
            await ctx.respond("There's no music playing to stop.")
def setup(bot):
    bot.add_cog(MusicCmd(bot))