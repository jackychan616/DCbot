import discord
from discord.ext import commands

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="Replies with Pong!")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong!")

# Setup function
async def setup(bot):
    print("BaseCog setup invoked")
    await bot.add_cog(BaseCog(bot))