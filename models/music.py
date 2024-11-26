
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