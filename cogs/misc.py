import discord
from discord.ext import commands
import voxelbotutils as vbu


class Misc(vbu.Cog):

    def __init__(self, bot):
        self.bot = bot

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def stab(self, ctx:commands.Context, user: discord.User = None):
        """
        This command has a fish stab a user.
        """
        if user.id == ctx.author.id:
            return await ctx.send("Your fish is too loyal to stab you!")
        await ctx.send(f"Your fish stabs {user.mention} with a knife, nice!", file=discord.File("C:/Users/JT/Pictures/Aqua/assets/images/background/stab.gif"))


def setup(bot):
    bot.add_cog(Misc(bot))
