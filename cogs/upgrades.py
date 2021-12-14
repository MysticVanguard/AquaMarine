from discord.ext import commands, vbu

from cogs import utils


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

    TIER_RANKS = {
        "rod_upgrade": {
            "bait_upgrade": [
                "line_upgrade",
                "lure_upgrade",
            ],
            "crate_chance_upgrade": [
                "weight_upgrade",
                "crate_tier_upgrade",
            ],
        },
        "bleach_upgrade": {
            "toys_upgrade": [
                "amazement_upgrade",
                "mutation_upgrade",
            ],
            "big_servings_upgrade": [
                "hygienic_upgrade",
                "feeding_upgrade",
            ],
        },
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
        fields = []
        for upgrade, level in upgrades[0].items():
            if upgrade != "user_id":
                tier += 1
                description = self.UPGRADE_DESCRIPTIONS[upgrade]
                name = " ".join(upgrade.split("_")).title()
                # Get the cost of an upgrade
                cost_string = f"{self.UPGRADE_COST_LIST[int(level)]:,} <:sand_dollar:877646167494762586>"

                if tier == 1:
                    parent_one = upgrade

                left_bar = "<:bar_L:886377903615528971>"
                start = ""
                start_two = ""
                emote = "<:bar_1:877646167184408617>"
                if tier == 2 or tier == 5:
                    cost_string = f"{self.UPGRADE_COST_LIST_TWO[int(level)]:,} <:sand_dollar:877646167494762586>"
                    parent_two = upgrade
                    if upgrades[0][parent_one] != 5:
                        description = "???"
                        name = "???"
                        cost_string = "???"
                    start = "<:straight_branch:886377903837806602>"
                    start_two = "<:straight:886377903879753728>"
                    emote = "<:bar_2:877646166823694437>"
                    left_bar = "<:bar_L_branch:886377903581986848>"
                    if tier == 5:
                        start = "<:branch:886377903825252402>"
                        start_two = "<:straight:886377903879753728>"
                elif tier == 6 or tier == 3:
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} <:sand_dollar:877646167494762586>"
                    if upgrades[0][parent_two] != 5:
                        description = "???"
                        name = "???"
                        cost_string = "???"
                    start = "<:__:886381017051586580><:straight_branch:886377903837806602>"
                    emote = "<:bar_3:877646167138267216>"
                    left_bar = "<:bar_L_straight:886379040884260884>"
                    if tier == 3:
                        start_two = "<:straight:886377903879753728><:straight:886377903879753728>"
                        start = "<:straight:886377903879753728><:straight_branch:886377903837806602>"
                    else:
                        start_two = "<:__:886381017051586580><:straight:886377903879753728>"
                elif tier == 4 or tier == 7:
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} <:sand_dollar:877646167494762586>"
                    if upgrades[0][parent_two] != 5:
                        description = "???"
                        name = "???"
                        cost_string = "???"
                    emote = "<:bar_3:877646167138267216>"
                    left_bar = "<:bar_L_straight:886379040884260884>"
                    if tier == 4:
                        start_two = "<:straight:886377903879753728><:straight:886377903879753728>"
                        start = "<:straight:886377903879753728><:branch:886377903825252402>"
                    else:
                        start_two = "<:__:886381017051586580><:straight:886377903879753728>"
                        start = "<:__:886381017051586580><:branch:886377903825252402>"
                # If they're fully upgraded
                if level == 5:
                    cost_string = "This Upgrade is fully upgraded."

                # Each level they have is a full bar emoji, up to 5 characters long
                emote_string_list.clear()  # Clear our emoji list first
                for _ in range(level):

                    emote_string_list.append(emote)

                while len(emote_string_list) < 5:
                    emote_string_list.append("<:bar_e:877646167146643556>")
                print(emote_string_list)

                # Generate the message to send

                progress_bar = f"{left_bar}{''.join(emote_string_list)}<:bar_R:877646167113080842>"
                nl = "\n"
                message.append(
                    (
                        f"{start}{progress_bar}",
                        f"{start_two}**{name}: (Lvl. {level}.): {cost_string}**{nl}{start_two}*{description}*",
                    )
                )
                print(len(progress_bar))

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
                """SELECT rod_upgrade, line_upgrade, crate_chance_upgrade, weight_upgrade, bait_upgrade,
                crate_tier_upgrade, lure_upgrade, feeding_upgrade, toys_upgrade, mutation_upgrade,
                amazement_upgrade, bleach_upgrade, big_servings_upgrade, hygienic_upgrade
                FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        max_level = 5
        rod_upgrades = [
            "line_upgrade",
            "bait_upgrade",
            "crate_chance_upgrade",
            "lure_upgrade",
            "crate_tier_upgrade",
            "weight_upgrade",
        ]
        bleach_upgrades = [
            "toys_upgrade",
            "big_servings_upgrade",
            "amazement_upgrade",
            "feeding_upgrade",
            "mutation_upgrade",
            "hygienic_upgrade",
        ]
        upgrade_base_name = upgrade.lower().removesuffix(" upgrade")
        upgrade = upgrade_base_name.replace(" ", "_") + "_upgrade"

        if upgrade not in upgrades[0].keys():
            return await ctx.send("That's not a valid upgrade.")

        if upgrade in rod_upgrades:
            if upgrades[0]["rod_upgrade"] != max_level:
                return await ctx.send("The Rod Upgrade needs upgraded first!")

            if upgrades[0]["bait_upgrade"] != max_level and upgrade in [
                "line_upgrade",
                "lure_upgrade",
            ]:
                return await ctx.send("The Bait Upgrade needs upgraded first!")

            if upgrades[0][
                "crate_chance_upgrade"
            ] != max_level and upgrade in [
                "weight_upgrade",
                "crate_tier_upgrade",
            ]:
                return await ctx.send(
                    "The Crate Chance Upgrade needs upgraded first!"
                )

        elif upgrade in bleach_upgrades:
            if upgrades[0]["bleach_upgrade"] != max_level:
                return await ctx.send(
                    "The Bleach Upgrade needs upgraded first!"
                )

            if upgrades[0]["toys_upgrade"] != max_level and upgrade in [
                "mutation_upgrade",
                "amazement_upgrade",
            ]:
                return await ctx.send("The Toys Upgrade needs upgraded first!")

            if upgrades[0][
                "big_servings_upgrade"
            ] != max_level and upgrade in [
                "feeding_upgrade",
                "hygienic_upgrade",
            ]:
                return await ctx.send(
                    "The Big Servings Upgrade needs upgraded first!"
                )

        # See how upgraded the user currently is
        upgrade_level = upgrades[0][upgrade]
        if upgrade_level == max_level:
            return await ctx.send("That upgrade is fully upgraded.")

        if upgrade in ("rod_upgrade", "bleach_upgrade"):
            upgrade_cost_list_used = self.UPGRADE_COST_LIST
        elif upgrade in (
            "crate_chance_upgrade",
            "bait_upgrade",
            "toys_upgrade",
            "big_servings_upgrade",
        ):
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_TWO
        else:
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_THREE

        if not await utils.check_price(
            self.bot,
            ctx.author.id,
            upgrade_cost_list_used[int(upgrade_level)],
            "balance",
        ):
            return await ctx.send(
                "You don't have enough Sand Dollars <:sand_dollar:877646167494762586> for this upgrade!"
            )

        # Upgrade them in the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""",
                upgrade_cost_list_used[int(upgrades[0][upgrade])],
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
    bot.add_cog(Upgrades(bot))
