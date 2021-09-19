import voxelbotutils as vbu
from discord.ext import commands

from cogs import utils


class Upgrades(vbu.Cog):

    UPGRADE_DESCRIPTIONS = {
        'rod_upgrade': 'Increases price caught fish sell for',
        'line_upgrade': 'Increases chance of catching two fish',
        'better_line_upgrade': 'Increases chance of catching two fish even more',
        'weight_upgrade': 'Increases the level fish are when caught',
        'bait_upgrade': 'Increases chance of catching rarer fish',
        'better_bait_upgrade': 'Increases chance of catching rarer fish even more',
        'lure_upgrade': 'Increases chance of catching a \'skinned\' fish',
        'feeding_upgrade': 'Increases fish lifespan after feeding',
        'toys_upgrade': 'Increases xp gained from entertaining',
        'better_toys_upgrade': 'Increases xp gained from entertaining even more',
        'amazement_upgrade': 'Increases chance of bonus level when entertaining',
        'bleach_upgrade': 'Increases the cleaning multiplier',
        'better_bleach_upgrade': 'Increases the cleaning multiplier even more',
        'hygienic_upgrade': 'Lessens the frequency of cleaning',

    }

    TIER_RANKS = {
        'rod_upgrade': {
            'line_upgrade': [
                'better_line_upgrade',
                'weight_upgrade'
            ],
            'bait_upgrade': [
                'better_bait_upgrade',
                'lure_upgrade'
            ]
        },
        'feeding_upgrade': {
            'toys_upgrade': [
                'better_toys_upgrade',
                'amazement_upgrade'
            ],
            'bleach_upgrade': [
                'better_bleach_upgrade',
                'hygienic_upgrade'
            ]
        }
    }
    UPGRADE_COST_LIST = (1000, 1500, 2500, 3000, 4000)
    UPGRADE_COST_LIST_TWO = (4000, 4500, 5500, 6000, 7000)
    UPGRADE_COST_LIST_THREE = (7000, 7500, 8500, 9000, 10000)

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
                """SELECT rod_upgrade, line_upgrade, better_line_upgrade, weight_upgrade, bait_upgrade, better_bait_upgrade, lure_upgrade, feeding_upgrade, toys_upgrade, better_toys_upgrade, amazement_upgrade, bleach_upgrade, better_bleach_upgrade, hygienic_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            if not upgrades:
                upgrades = await db("""INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""", ctx.author.id)

        # Build out output strings
        tier = 0
        tree_number = 0
        fields = []
        for upgrade, level in upgrades[0].items():
            tier += 1
            description = self.UPGRADE_DESCRIPTIONS[upgrade]
            name = ' '.join(upgrade.split('_')).title()
            # Get the cost of an upgrade
            cost_string = f"{self.UPGRADE_COST_LIST[int(level - 1)]:,} <:sand_dollar:877646167494762586>"


            if tier == 1:
                parent_one = upgrade




            left_bar = "<:bar_L:886377903615528971>"
            start = ""
            start_two = ""
            emote = "<:bar_1:877646167184408617>"
            if tier == 2 or tier == 5:
                cost_string = f"{self.UPGRADE_COST_LIST_TWO[int(level - 1)]:,} <:sand_dollar:877646167494762586>"
                parent_two = upgrade
                if upgrades[0][parent_one] != 5:
                    description = "???"
                    name = "???"
                    cost_string = "???"
                start = '<:straight_branch:886377903837806602>'
                start_two = "<:straight:886377903879753728>"
                emote = "<:bar_2:877646166823694437>"
                left_bar = "<:bar_L_branch:886377903581986848>"
                if tier == 5:
                    start = '<:branch:886377903825252402>'
                    start_two = "<:straight:886377903879753728>"
            elif tier == 6 or tier == 3:
                cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level - 1)]:,} <:sand_dollar:877646167494762586>"
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
                cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level - 1)]:,} <:sand_dollar:877646167494762586>"
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
            message.append((f"{start}{progress_bar} *{description}*", f"{start_two}**{name}: (Lvl. {level}.): {cost_string}**"))
            print(len(progress_bar))

            if tier == 7:
                message.append(("** **", "** **"))
                tree_number += 1
                tier = 0

        # And send our message
        embed = vbu.Embed()
        for message_data in message:
            embed.add_field(name=message_data[1], value=message_data[0], inline=False)
        await ctx.send(embed=embed)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx: commands.Context, *, upgrade: str):
        """
        Upgrade one of your items.
        """

        # Grab the user's current upgrades
        async with self.bot.database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, line_upgrade, better_line_upgrade, weight_upgrade, bait_upgrade, better_bait_upgrade, lure_upgrade, feeding_upgrade, toys_upgrade, better_toys_upgrade, amazement_upgrade, bleach_upgrade, better_bleach_upgrade, hygienic_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        # Make sure the upgrade is valid
        upgraded = f"{upgrade.replace(' ', '_')}_upgrade"
        if upgraded not in upgrades[0].keys():
            return await ctx.send("That's not a valid upgrade.")
        if upgraded in ['line_upgrade', 'bait_upgrade', 'better_bait_upgrade', 'lure_upgrade', 'better_line_upgrade', 'weight_upgrade']:
            if upgrades[0]['rod_upgrade'] != 5:
                return await ctx.send("The Rod Upgrade needs upgraded first!")
            if upgrades[0]['line_upgrade'] != 5 and upgraded in ['better_line_upgrade', 'weight_upgrade']:
                return await ctx.send("The Line Upgrade needs upgraded first!")
            if upgrades[0]['bait_upgrade'] != 5 and upgraded in ['lure_upgrade', 'better_bait_upgrade']:
                return await ctx.send("The Bait Upgrade needs upgraded first!")
        if upgraded in ['toys_upgrade', 'better_toys_upgrade', 'amazement_upgrade', 'bleach_upgrade', 'better_bleach_upgrade', 'hygienic_upgrade']:
            if upgrades[0]['feeding_upgrade'] != 5:
                return await ctx.send("The Feeding Upgrade needs upgraded first!")
            if upgrades[0]['toys_upgrade'] != 5 and upgraded in ['better_toys_upgrade', 'amazement_upgrade']:
                return await ctx.send("The Toys Upgrade needs upgraded first!")
            if upgrades[0]['bleach_upgrade'] != 5 and upgraded in ['better_bleach_upgrade', 'hygienic_upgrade']:
                return await ctx.send("The Bleach Upgrade needs upgraded first!")

        # See how upgraded the user currently is
        upgrade_level = upgrades[0][upgraded]
        if upgrade_level == 5:
            return await ctx.send("That upgrade is fully upgraded.")
        if upgraded in ('rod_upgrade', 'feeding_upgrade'):
            upgrade_cost_list_used = self.UPGRADE_COST_LIST
        elif upgraded in ('line_upgrade', 'bait_upgrade', 'toys_upgrade', 'bleach_upgrade'):
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_TWO
        else:
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_THREE

        if not await utils.check_price(self.bot, ctx.author.id, upgrade_cost_list_used[int(upgrade_level) - 1], 'balance'):
            return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:877646167494762586> for this upgrade!")

        # Upgrade them in the database
        async with self.bot.database() as db:
            await db("""UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", upgrade_cost_list_used[int(upgrades[0][upgraded])- 1], ctx.author.id)
            await db("""UPDATE user_upgrades SET {0}=user_upgrades.{0}+1 WHERE user_id = $1""".format(upgraded), ctx.author.id)

        # And bam
        await ctx.send(f"{upgrade.title()} has been upgraded for {upgrade_cost_list_used[upgrade_level - 1]:,}!")


def setup(bot):
    bot.add_cog(Upgrades(bot))
