import discord
import utils
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def fish(self, ctx:commands.Context):
        pass

def setup(bot):
    bot.add_cog(MembersCog(bot))
