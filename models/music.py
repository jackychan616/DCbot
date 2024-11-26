
class Music():
    def __init__(self, bot,message):
        self.bot = bot
        self.message = message
    async def SkipSong(self):
        print("SkipSong")
        if self.message.guild.voice_client and self.message.guild.voice_client.is_playing():
            self.message.guild.voice_client.stop()
            await self.message.reply("Skipped")        
        else:
            await self.message.reply("No song playing")        
    async def JoinUserVC(self):
        if self.message.author.voice.channel != None and self.message.guild.voice_client != self.message.author.voice.channel:
            await self.message.author.voice.channel.connect()
            return await self.message.reply("Already joined")
        await self.message.reply("You are not in VC or Aleady joined VC !")
    async def PlaySong(self):

        pass
