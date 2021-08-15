import voxelbotutils as vbu
from discord.ext import commands

from cogs import utils


class Upgrades(vbu.Cog):

    UPGRADE_DESCRIPTIONS = {
        'line_upgrade': 'This upgrade makes your chance of getting two fish in one cast higher.',
        'rod_upgrade': 'This upgrade makes the price a fish sells for when caught increase.',
        'bait_upgrade': 'This upgrade makes it so your chances of catching higher rarity fish increase.',
        'lure_upgrade': 'This upgrade increases the chance of getting an inverted or golden fish.',
        'weight_upgrade': 'This upgrade increases the possible level a caught fish can be.'
    }
    UPGRADE_COST_LIST = (125, 250, 500, 1000, 2000,)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrades(self, ctx: commands.Context):
        """
        Show you your upgrades and the price of the next level.
        """

        # The output that we want to build
        message = []  # A list of text to send
        emote_string_list = []  # Their emoji progress bar

        # Grab their upgrades from the database
        async with self.bot.database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            if not upgrades:
                upgrades = await db("""INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""", ctx.author.id)

        # Build out output strings
        for upgrade, level in upgrades[0].items():

            # Each level they have is a full bar emoji, up to 5 characters long
            emote_string_list.clear()  # Clear our emoji list first
            for _ in range(level):
                emote_string_list.append("<:full_upgrade_bar:865028622766702602>")
            while len(emote_string_list) < 5:
                emote_string_list.append("<:empty_upgrade_bar:865028614561988649>")

            # Get the cost of an upgrade
            cost_string = f"Costs {self.UPGRADE_COST_LIST[int(level - 1)]} to upgrade."

            # If they're fully upgraded
            if level == 5:
                # emote_string_list = ["<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>"]
                cost_string = "This Upgrade is fully upgraded."

            # Generate the message to send
            progress_bar = f"<:left_upgrade_bar:865028588192661504>{''.join(emote_string_list)}<:right_upgrade_bar:865028605863919616>"
            message.append(
                f"{progress_bar} **{' '.join(upgrade.split('_')).title()}: Lvl. {level}. {cost_string}**\n*{self.UPGRADE_DESCRIPTIONS[upgrade]}*",
            )

        # And send our message
        await ctx.send('\n'.join(message))

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx: commands.Context, upgrade: str):
        """
        Upgrade one of your items.
        """

        # Grab the user's current upgrades
        async with self.bot.database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        # Make sure the upgrade is valid
        upgraded = f"{upgrade}_upgrade"
        if upgraded not in upgrades[0].keys():
            return await ctx.send("That's not a valid upgrade.")

        # See how upgraded the user currently is
        upgrade_level = upgrades[0][upgraded]
        if upgrade_level == 5:
            return await ctx.send("That upgrade is fully upgraded.")
        if not await utils.check_price(self.bot, ctx.author.id, self.UPGRADE_COST_LIST[int(upgrade_level) - 1]):
            return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:852057443503964201> for this upgrade!")

        # Upgrade them in the database
        async with self.bot.database() as db:
            await db("""UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", self.UPGRADE_COST_LIST[int(upgrades[0][upgraded])- 1], ctx.author.id)
            await db("""UPDATE user_upgrades SET {0}=user_upgrades.{0}+1 WHERE user_id = $1""".format(upgraded), ctx.author.id)

        # And bam
        await ctx.send(f"{upgrade.title()} has been upgraded for {self.UPGRADE_COST_LIST[upgrade_level - 1]:,}!")


def setup(bot):
    bot.add_cog(Upgrades(bot))
