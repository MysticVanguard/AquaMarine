import discord
from discord.ext import commands
import voxelbotutils as vbu


class Misc(vbu.Cog):

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def stab(self, ctx: commands.Context, user: discord.User = None):
        """
        This command has a fish stab a user.
        """

        if user.id == ctx.author.id:
            return await ctx.send("Your fish is too loyal to stab you!")
        await ctx.send(
            f"Your fish stabs {user.mention} with a knife, nice!",
            file=discord.File("C:/Users/JT/Pictures/Aqua/assets/images/background/stab.gif"),
        )

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def bug(self, ctx: commands.Context, command: str, *, info: str):
        """
        This command sends a bug report to the support server.
        """
        user = ctx.author
        channel = self.bot.get_channel(877446487087415337)
        await channel.send(
            f"From: {user.mention}\n"
            f"**{command}**: {info}",
            allowed_mentions=discord.AllowedMentions.none()
            )
        await ctx.send("Bug report sent!")

def setup(bot):
    bot.add_cog(Misc(bot))
