import discord
from discord.ext import commands, vbu


class Misc(vbu.Cog):
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def stab(self, ctx: commands.Context, user: discord.User):
        """
        This command has a fish stab a user.
        """

        if user.id == ctx.author.id:
            return await ctx.send("Your fish is too loyal to stab you!")
        await ctx.send(
            f"Your fish stabs {user.mention} with a knife, nice!",
            file=discord.File(
                "C:/Users/JT/Pictures/Aqua/assets/images/background/stab.gif"
            ),
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def bug(self, ctx: commands.Context, command: str, *, info: str):
        """
        This command sends a bug report to the support server.
        """

        user = ctx.author
        channel: discord.TextChannel = self.bot.get_channel(
            877446487087415337
        )  # type: ignore
        await channel.send(
            f"From: {user.mention}\n**{command}**: {info}",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await ctx.send("Bug report sent!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def support(self, ctx: commands.Context):
        """
        This command sends the server link to the support server.
        """

        await ctx.send("https://discord.gg/FUyr8QmrD8")


def setup(bot):
    bot.add_cog(Misc(bot))
