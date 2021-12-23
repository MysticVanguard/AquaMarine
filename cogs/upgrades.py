from discord.ext import commands, vbu

from cogs import utils
from cogs.utils import EMOJIS


class Upgrades(vbu.Cog):

    UPGRADE_DESCRIPTIONS = {
        "rod_upgrade": "Increases the price a caught fish sells for",
        "line_upgrade": "Increases the chance of catching two fish in one cast",
        "crate_chance_upgrade": "Increases chance of catching a crate when fishing",
        "weight_upgrade": "Increases the level fish are when caught",
        "bait_upgrade": "Increases the chance of catching rarer fish when fishing",
        "crate_tier_upgrade": "Increases the tier of the crate caught",
        "lure_upgrade": "Increases the chance of catching a special fish when fishing",
        "feeding_upgrade": "Increases how long fish will live after being fed",
        "toys_upgrade": "Increases the xp gained from entertaining",
        "mutation_upgrade": "Increases the chance of a fish mutating to a special fish during cleaning",
        "amazement_upgrade": "Increases chance of bonus level when entertaining",
        "bleach_upgrade": "Increases the cleaning multiplier",
        "big_servings_upgrade": "Increases chance of a fish not eating food when they are fed",
        "hygienic_upgrade": "Lessens the frequency of cleaning, while giving a multiplier equal to the lost time",
    }

    # TIER 3
    BAIT_UPGRADES = ["line_upgrade", "lure_upgrade"]
    CRATE_CHANCE_UPGRADES = ["weight_upgrade", "crate_tier_upgrade"]
    TOYS_UPGRADES = ["amazement_upgrade", "mutation_upgrade"]
    BIG_SERVINGS_UPGRADES = ["hygienic_upgrade", "feeding_upgrade"]
    TIER_3 = (
        BAIT_UPGRADES
        + CRATE_CHANCE_UPGRADES
        + TOYS_UPGRADES
        + BIG_SERVINGS_UPGRADES
    )

    # TIER 2
    ROD_UPGRADES = {
        "bait_upgrade": BAIT_UPGRADES,
        "crate_chance_upgrade": CRATE_CHANCE_UPGRADES,
    }
    BLEACH_UPGRADES = {
        "toys_upgrade": TOYS_UPGRADES,
        "big_servings_upgrade": BIG_SERVINGS_UPGRADES,
    }
    TIER_2 = ROD_UPGRADES | BLEACH_UPGRADES

    # TIER 1
    TIER_1 = {
        "rod_upgrade": ROD_UPGRADES,
        "bleach_upgrade": BLEACH_UPGRADES,
    }

    UPGRADE_COST_LIST = (1000, 2000, 3000, 4000, 5000, 5000)
    UPGRADE_COST_LIST_TWO = (10000, 20000, 30000, 40000, 50000, 50000)
    UPGRADE_COST_LIST_THREE = (100000, 200000, 300000, 400000, 500000, 500000)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrades(self, ctx: commands.Context):
        """
        Show you your upgrades and the price of the next level.
        """

        # The output that we want to build
        message = []  # A list of text to send
        emote_string_list = []  # Their emoji progress bar

        # Grab their upgrades from the database
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, line_upgrade, lure_upgrade, crate_chance_upgrade, weight_upgrade,
                crate_tier_upgrade, bleach_upgrade, toys_upgrade, amazement_upgrade, mutation_upgrade,
                big_servings_upgrade, hygienic_upgrade, feeding_upgrade
                FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            if not upgrades:
                upgrades = await db(
                    """INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""",
                    ctx.author.id,
                )

        # Build out output strings
        tier = 0
        tree_number = 0
        unknown_str = "???"
        for upgrade, level in upgrades[0].items():
            if upgrade != "user_id":
                tier += 1
                description = self.UPGRADE_DESCRIPTIONS[upgrade]
                name = " ".join(upgrade.split("_")).title()
                # Get the cost of an upgrade
                cost_string = f"{self.UPGRADE_COST_LIST[int(level)]:,} {EMOJIS['sand_dollar']}"

                if tier == 1:
                    parent_one = upgrade

                left_bar = EMOJIS["bar_L"]
                start = ""
                start_two = ""
                emote = EMOJIS["bar_1"]
                if tier in (2, 5):
                    cost_string = f"{self.UPGRADE_COST_LIST_TWO[int(level)]:,} {EMOJIS['sand_dollar']}"
                    parent_two = upgrade
                    if upgrades[0][parent_one] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str
                    start = EMOJIS["straight_branch"]
                    start_two = EMOJIS["straight"]
                    emote = EMOJIS["bar_2"]
                    left_bar = EMOJIS["bar_L_branch"]
                    if tier == 5:
                        start = EMOJIS["branch"]
                        start_two = EMOJIS["straight"]
                elif tier in (3, 6):
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} {EMOJIS['sand_dollar']}"
                    if upgrades[0][parent_two] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str
                    start = f"{EMOJIS['empty']}{EMOJIS['straight_branch']}"
                    emote = EMOJIS["bar_3"]
                    left_bar = EMOJIS["bar_L_straight"]
                    if tier == 3:
                        start_two = f"{EMOJIS['straight']}{EMOJIS['straight']}"
                        start = (
                            f"{EMOJIS['straight']}{EMOJIS['straight_branch']}"
                        )
                    else:
                        start_two = f"{EMOJIS['empty']}{EMOJIS['straight']}"
                elif tier in (4, 7):
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} {EMOJIS['sand_dollar']}"
                    if upgrades[0][parent_two] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str
                    emote = EMOJIS["bar_3"]
                    left_bar = EMOJIS["bar_L_straight"]
                    if tier == 4:
                        start_two = f"{EMOJIS['straight']}{EMOJIS['straight']}"
                        start = f"{EMOJIS['straight']}{EMOJIS['branch']}"
                    else:
                        start_two = f"{EMOJIS['empty']}{EMOJIS['straight']}"
                        start = f"{EMOJIS['empty']}{EMOJIS['branch']}"
                # If they're fully upgraded
                if level == 5:
                    cost_string = "This Upgrade is fully upgraded."

                # Each level they have is a full bar emoji, up to 5 characters long
                emote_string_list.clear()  # Clear our emoji list first
                for _ in range(level):

                    emote_string_list.append(emote)

                while len(emote_string_list) < 5:
                    emote_string_list.append(EMOJIS["bar_e"])

                # Generate the message to send

                progress_bar = (
                    f"{left_bar}{''.join(emote_string_list)}{EMOJIS['bar_R']}"
                )
                new_line = "\n"
                message.append(
                    (
                        f"{start}{progress_bar}",
                        f"{start_two}**{name}: (Lvl. {level}.): {cost_string}**{new_line}{start_two}*{description}*",
                    )
                )

                if tier == 7:
                    message.append(("** **", "** **"))
                    tree_number += 1
                    tier = 0

        # And send our message
        embed = vbu.Embed()
        for time, message_data in enumerate(message):
            if time == 0:
                embed.add_field(
                    name="The Way of the Fish",
                    value="These upgrades have to do with fishing",
                    inline=False,
                )
            elif time == 8:
                embed.add_field(
                    name="The Way of the Tank",
                    value="These upgrades have to do with owning fish in aquariums",
                    inline=False,
                )
            embed.add_field(
                name=message_data[1], value=message_data[0], inline=False
            )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx: commands.Context, *, upgrade: str):
        """
        Upgrade one of your items.
        """

        # Grab the user's current upgrades
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, line_upgrade, crate_chance_upgrade,
                weight_upgrade, bait_upgrade, crate_tier_upgrade,
                lure_upgrade, feeding_upgrade, toys_upgrade,
                mutation_upgrade, amazement_upgrade, bleach_upgrade,
                big_servings_upgrade, hygienic_upgrade
                FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        upgrades = upgrades[0]
        upgrade_base_name = upgrade.lower().removesuffix(" upgrade")
        upgrade = upgrade_base_name.replace(" ", "_") + "_upgrade"
        max_level = 5

        def fully_leveled(item):
            return item == max_level

        def upgrade_error(msg_text):
            msg_text = msg_text.replace("_", " ").title()
            error_msg = f"The {msg_text} needs upgraded first!"
            return error_msg

        # Check for valid upgrade and dependencies of upgrade tiers
        if upgrade in self.TIER_1:
            upgrade_cost_list_used = self.UPGRADE_COST_LIST
        elif upgrade in self.TIER_2:
            # Find parent tier and check if it's upgraded
            parent = [key for key, val in self.TIER_1 if upgrade in val][0]
            if not fully_leveled(upgrades[parent]):
                return await ctx.send(upgrade_error(parent))
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_TWO
        elif upgrade in self.TIER_3:
            # Find parent tier and check if it's upgraded
            parent = [key for key, val in self.TIER_2 if upgrade in val][0]
            if not fully_leveled(upgrades[parent]):
                return await ctx.send(upgrade_error(parent))
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_THREE
        else:
            return await ctx.send("That's not a valid upgrade.")

        # Check level of validated upgrade
        upgrade_level = upgrades[upgrade]
        if fully_leveled(upgrade_level):
            return await ctx.send("That upgrade is fully upgraded.")

        if not await utils.check_price(
            self.bot,
            ctx.author.id,
            upgrade_cost_list_used[int(upgrade_level)],
            "balance",
        ):
            return await ctx.send(
                f"You don't have enough Sand Dollars {EMOJIS['sand_dollar']} for this upgrade!"
            )

        # Upgrade them in the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""",
                upgrade_cost_list_used[int(upgrades[upgrade])],
                ctx.author.id,
            )
            await db(
                f"""UPDATE user_upgrades SET {upgrade}=user_upgrades.{upgrade}+1 WHERE user_id = $1""",
                ctx.author.id,
            )

        # And bam
        await ctx.send(
            f"You bought the Level {upgrade_level + 1} "
            f"{upgrade_base_name.title()} Upgrade for "
            f"{upgrade_cost_list_used[upgrade_level]:,}!"
        )


def setup(bot):
    """Bot Setup"""
    bot.add_cog(Upgrades(bot))
