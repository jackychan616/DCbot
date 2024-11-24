import discord
from discord.ext import commands
from api.gc_tts import TTS
guild_id = ["1162672034262814728","1181528878993395712"]       

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="Replies with Pong!")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong!")
    @discord.slash_command(name="test",guild_ids = guild_id)
    async def test(self,ctx):
        await TTS(text = "hi",Lang_code="en").getAudio()
        vc = ctx.voice_client
        vc.play(discord.FFmpegPCMAudio("output.mp3"))
# Setup function
def setup(bot):
    print("BaseCog setup invoked")
    bot.add_cog(BaseCog(bot))