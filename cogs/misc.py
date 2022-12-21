import discord
from discord.ext import commands, vbu, tasks


class Misc(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.reset_fish_pools.start()

    # When the cog is turned off, turn the loop off
    def cog_unload(self):
        self.reset_fish_pools.cancel()

    # Every hour, everyone gets a cast as long as they have less than 50
    @tasks.loop(hours=168)
    async def reset_fish_pools(self):
        async with vbu.Database() as db:
            await db("""DELETE FROM fish_pool_location""")
            await db("""INSERT INTO fish_pool_location (banggai_cardinalfish_count) VALUES (100)""")

    # Wait until the bot is on and ready and not just until the cog is on
    @reset_fish_pools.before_loop
    async def before_reset_fish_pools(self):
        await self.bot.wait_until_ready()

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    type=discord.ApplicationCommandOptionType.user,
                    description="The user stabbed"
                ),
            ]
        )
    )
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

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="command",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The command that produced the the bug"
                ),
                discord.ApplicationCommandOption(
                    name="info",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The info about the bug you want to submit"
                )
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True)
    async def bug(self, ctx: commands.Context, command: str, *, info: str):
        """
        This command sends a bug report to the support server.
        """

        # Set the message to send to
        channel: discord.TextChannel = self.bot.get_channel(877446487087415337)

        # Send the bug they reported to that channel with their user
        await channel.send(
            f"From: {ctx.author.mention}\n**{command}**: {info}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

        # let them know the bug report was sent
        await ctx.send("Bug report sent!")

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.bot_has_permissions(send_messages=True)
    async def support(self, ctx: commands.Context):
        """
        This command sends the server link to the support server.
        """

        # Sends the link for the support server
        await ctx.send("https://discord.gg/FUyr8QmrD8")

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.bot_has_permissions(send_messages=True)
    async def vote_x(self, ctx: commands.Context):
        """
        This command sends the voting link.
        """

        # Sends the link for the support server
        embed = discord.Embed(title="Vote for AquaMarine!")
        embed.add_field(
            name="**Top.gg**", value=f"[Vote Here!](https://top.gg/bot/840956686743109652/vote)")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
