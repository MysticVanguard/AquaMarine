import discord
from discord.ext import commands, vbu, tasks


class Misc(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def stab(self, ctx: commands.Context, user: discord.User):
        """
        This command has a fish stab a user.
        """

        # Make it so you can't stab yourself
        if user.id == ctx.author.id:
            return await ctx.send("Your fish is too loyal to stab you!")

        # Send the gif and the say they stabbed the person
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

        # Set the user to the person using the command
        user = ctx.author

        # Set the message to send to
        channel: discord.TextChannel = self.bot.get_channel(
            877446487087415337
        )

        # Send the bug they reported to that channel with their user
        await channel.send(
            f"From: {user.mention}\n**{command}**: {info}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

        # let them know the bug report was sent
        await ctx.send("Bug report sent!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def support(self, ctx: commands.Context):
        """
        This command sends the server link to the support server.
        """

        # Sends the link for the support server
        await ctx.send("https://discord.gg/FUyr8QmrD8")


def setup(bot):
    bot.add_cog(Misc(bot))
