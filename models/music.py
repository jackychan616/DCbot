import yt_dlp as youtube_dl
from urlextract import URLExtract
from youtube_search import YoutubeSearch
import discord
from temp.playlist import playlist
guild_id = ["1162672034262814728","1181528878993395712"]       

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
youtube_dl.utils.bug_reports_message = lambda: ""

async def SearchSongWithList(songlist):
        songlist_url = []
        for song in songlist:
            url = YoutubeSearch(song,max_results=10).to_dict()
            url = "https://www.youtube.com/" + url[0]["url_suffix"]
            songlist_url.append(url)
        return songlist_url  
class MuiscCore():
    def __init__(self):
        self.playlist = playlist
    async def getSong(self,ctx,song):
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(song, download=False)
                url2 = info['url']
                title = info.get('title', 'Unknown Title')
            except Exception as e:
                await ctx.reply(e)
                return
        return {"url":url2,"title":title}
    def next_song(self,ctx):
            guild = ctx.guild.id
            if guild in self.playlist and self.playlist[guild]:
                next_url,next_title = self.playlist[guild].pop(0)
                vc = ctx.guild.voice_client
                self.bot.loop.create_task(self.playSong(ctx=ctx, vc=vc, url=next_url, title=next_title))
                
    async def playSong(self,ctx,url,title,vc):
        data = await self.getSong(ctx,url)
        url = data["url"]
        title = data["title"]
        
        # await self.NextSongNoti(ctx=ctx,title = title)
        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=lambda e: self.next_song(ctx = ctx))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = 0.5
        await ctx.reply(f"Now playing: {title}")
class Music():
    def __init__(self, bot,message,arguments=None):
        self.bot = bot
        self.message = message
        self.arguments = arguments
        self.playlist = playlist
        self.getSong = MuiscCore().getSong
    async def SkipSong(self):
        print("SkipSong")
        if self.message.guild.voice_client and self.message.guild.voice_client.is_playing():
            self.message.guild.voice_client.stop()
            await self.message.reply("Skipped")        
        else:
            await self.message.reply("No song playing")        
    async def JoinUserVC(self):
        try:
            if self.message.author.voice.channel != None and self.message.guild.voice_client != self.message.author.voice.channel:
                await self.message.author.voice.channel.connect()
                return await self.message.reply("Already joined")
        except:
            await self.message.reply("You are not in VC or Aleady joined VC !")
    async def PlaySong(self):
        song = self.arguments["Song_name"]
        url = YoutubeSearch(song,max_results=10).to_dict()
        url = "https://www.youtube.com/" + url[0]["url_suffix"]
        vc = self.message.guild.voice_client
        guild = self.message.guild.id
        if vc.is_playing():
            data = await MuiscCore().getSong(ctx= self.message,song = url)
            await self.message.reply("Song is already playing")
            return self.playlist[guild].append((url,data["title"]))
        return await MuiscCore().playSong(ctx=self.message,url = url,title = song,vc = vc)
    async def PlayListOfSongs(self):
        songlist = eval(self.arguments["Song_list"])
        songlist_url = await SearchSongWithList(songlist)
        vc = self.message.guild.voice_client
        guild = self.message.guild.id
        if guild not in self.playlist:
            self.playlist[guild] = []
        if vc.is_playing():
            for song in songlist_url:
                data = await MuiscCore().getSong(ctx= self.message,song = song)
                self.playlist[guild].append((song,data["title"]))
            await self.message.reply("Songs added to playlist")
            return
        else:
            i = 0
            for song in songlist_url:
                self.playlist[guild].append((song, songlist[i]))
                i += 1
            return await MuiscCore().playSong(ctx=self.message,url = songlist_url[0],title = songlist[0],vc = vc)