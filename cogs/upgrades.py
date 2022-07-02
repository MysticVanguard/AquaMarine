from discord.ext import commands, vbu

from cogs import utils
from cogs.utils import EMOJIS
from PIL import Image
import random
import string
import discord


class Upgrades(vbu.Cog):

    # The upgrades with their descriptions
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
        "mutation_upgrade": "Increases chance of a fish getting a skin while cleaning",
        "amazement_upgrade": "Increases chance of bonus level when entertaining",
        "bleach_upgrade": "Increases the cleaning multiplier",
        "big_servings_upgrade": "Increases chance of a fish not eating food when they are fed",
        "hygienic_upgrade": "Lessens the frequency of cleaning, and gives multiplier to compensate",
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

    # The lost of costs for the three tiers
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
        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")
        async with vbu.Database() as db:
            upgrades = await utils.user_upgrades_db_call(ctx.author.id)

        # Find the positions for the different upgrades
        positions = [(2140, 910), (1300, 1070), (1310, 1260), (1710, 1080), (2200, 1470),
                     (1760, 1290), (2180, 1450), (2670,
                                                  170), (240, 210), (840, 110),
                     (550, 1460), (840, 750), (1930, 190), (1020, 1290)]

        # Makes a list of the upgrades names
        list_of_upgrades = [single for single in upgrades[0].keys()]

        # Create an id for the image
        id = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(10)
        )

        # Set the file prefix, shadow path, and file name
        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
        shadow = f"{file_prefix}/background/Room Walls/shadow-export.png"
        file_name = f"{file_prefix}/background/Room Walls/Upgrades_Wall/User Walls/{id}user_upgrade_room.png"

        # Open the shadow and background, make a copy of background
        shadow = Image.open(shadow).convert("RGBA")
        background = Image.open(
            f"{file_prefix}/background/Room Walls/Upgrade_Wall-export.png"
        ).convert("RGBA")
        new_background = background.copy()

        # For each upgrade open the upgrade at it's tier and paste it to the background
        for i, upgrade in enumerate(upgrades[0]):
            if i == 0:
                continue
            added_upgrade = Image.open(
                f"{file_prefix}/background/Room Walls/Upgrades_Wall/{list_of_upgrades[i]}_tier_{upgrades[0][list_of_upgrades[i]]+1}-export.png").convert("RGBA")
            new_background.paste(added_upgrade, positions[i-1], added_upgrade)

        # Paste the shadow on top finally
        new_background.paste(shadow, (0, 0), shadow)

        # Save the background as a png with the file name and send it
        new_background.save(file_name, format="PNG")
        await ctx.send(file=discord.File(file_name))

        # Set up variables
        tier = 0
        tree_number = 0
        unknown_str = "???"

        # For each upgrade...
        for upgrade, level in upgrades[0].items():

            # If it isnt the user id
            if upgrade != "user_id":

                # Set the tier to 1 more than it was, set the description and name
                tier += 1
                description = self.UPGRADE_DESCRIPTIONS[upgrade]
                name = " ".join(upgrade.split("_")).title()

                # Get the cost of an upgrade
                cost_string = f"{self.UPGRADE_COST_LIST[int(level)]:,} {EMOJIS['sand_dollar']}"

                # If its the first tier its also the parent upgrade
                if tier == 1:
                    parent_one = upgrade

                # Set up variables upgrade specific
                left_bar = EMOJIS["bar_L"]
                start = ""
                start_two = ""
                emote = EMOJIS["bar_1"]

                # If the tier is 2 or 5 it's in the second tier of upgrades
                if tier in (2, 5):

                    # Set the cost with the second list and set it to the second parent upgrade
                    cost_string = f"{self.UPGRADE_COST_LIST_TWO[int(level)]:,} {EMOJIS['sand_dollar']}"
                    parent_two = upgrade

                    # If they don't have the full upgrade of the previous one, make them unknown
                    if upgrades[0][parent_one] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str

                    # Set the start emotes to the correct emojis
                    start = EMOJIS["straight_branch"]
                    start_two = EMOJIS["straight"]
                    emote = EMOJIS["bar_2"]
                    left_bar = EMOJIS["bar_L_branch"]

                    # If its tier 5 set some more emojis
                    if tier == 5:
                        start = EMOJIS["branch"]
                        start_two = EMOJIS["straight"]

                # If its in tiers 3 or 6 (the first set of tier 3)
                elif tier in (3, 6):

                    # Set the cost of upgrade to cost list three
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} {EMOJIS['sand_dollar']}"

                    # If the parent isnt fully upgraded, set these to unknown
                    if upgrades[0][parent_two] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str

                    # Set variables to the correct emotes
                    start = f"{EMOJIS['bar_empty']}{EMOJIS['straight_branch']}"
                    emote = EMOJIS["bar_3"]
                    left_bar = EMOJIS["bar_L_straight"]

                    # If the tier is 3 set some other correct emotes
                    if tier == 3:
                        start_two = f"{EMOJIS['straight']}{EMOJIS['straight']}"
                        start = (
                            f"{EMOJIS['straight']}{EMOJIS['straight_branch']}"
                        )

                    # If not set another correct emote
                    else:
                        start_two = f"{EMOJIS['bar_empty']}{EMOJIS['straight']}"

                # Else if its in tier 4 or 7 (in the second set of tier 3 upgrades)
                elif tier in (4, 7):

                    # Set the cost of upgrade to cost list three
                    cost_string = f"{self.UPGRADE_COST_LIST_THREE[int(level)]:,} {EMOJIS['sand_dollar']}"

                    # If the parent isnt fully upgraded, set these to unknown
                    if upgrades[0][parent_two] != 5:
                        description = unknown_str
                        name = unknown_str
                        cost_string = unknown_str

                    # Set variables to the correct emotes
                    emote = EMOJIS["bar_3"]
                    left_bar = EMOJIS["bar_L_straight"]

                    # If the tier is 4 set some other correct emotes
                    if tier == 4:
                        start_two = f"{EMOJIS['straight']}{EMOJIS['straight']}"
                        start = f"{EMOJIS['straight']}{EMOJIS['branch']}"

                    # If not set other correct emotes
                    else:
                        start_two = f"{EMOJIS['bar_empty']}{EMOJIS['straight']}"
                        start = f"{EMOJIS['bar_empty']}{EMOJIS['branch']}"

                # If they're fully upgraded
                if level == 5:
                    cost_string = "Fully upgraded."

                # Each level they have is a full bar emoji, up to 5 characters long
                emote_string_list.clear()  # Clear our emoji list first
                for _ in range(level):

                    emote_string_list.append(emote)

                while len(emote_string_list) < 5:
                    emote_string_list.append(EMOJIS["bar_e"])

                # Set up the progress bar
                progress_bar = (
                    f"{left_bar}{''.join(emote_string_list)}{EMOJIS['bar_R']}"
                )

                # New line for f strings
                new_line = "\n"

                # Set up the message for the upgrade
                message.append(
                    (
                        f"{start}{progress_bar}",
                        f"{start_two}**{name}: (Lvl. {level}.): {cost_string}**{new_line}{start_two}*{description}*",
                    )
                )

                # If its the last tier of the tree
                if tier == 7:
                    # Append some empty spaces
                    message.append(("** **", "** **"))

                    # Set tree to 2 and tier back to 0
                    tree_number += 1
                    tier = 0

        # Set up the embed with titles for each field
        for time, message_data in enumerate(message):
            if time <= 7:
                if time == 0:
                    embed = vbu.Embed()
                    embed.add_field(
                        name="The Way of the Fish",
                        value="These upgrades have to do with fishing",
                        inline=False,
                    )
                embed.add_field(
                    name=message_data[1], value=message_data[0], inline=False
                )
            if time > 7:
                if time == 8:
                    embed_2 = vbu.Embed()
                    embed_2.add_field(
                        name="The Way of the Tank",
                        value="These upgrades have to do with owning fish in aquariums",
                        inline=False,
                    )
                embed_2.add_field(
                    name=message_data[1], value=message_data[0], inline=False
                )
        # Send the embed
        await ctx.send(embed=embed)
        await ctx.send(embed=embed_2)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx: commands.Context, *, upgrade: str):
        """
        Upgrade one of your items.
        """

        # Grab the user's current upgrades
        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")
        async with vbu.Database() as db:
            upgrades = await utils.user_upgrades_db_call(ctx.author.id)

        # Set up their upgrades and let them enter the name of the upgrade with or without upgrade
        upgrades = upgrades[0]
        upgrade_base_name = upgrade.lower().removesuffix(" upgrade")
        upgrade = upgrade_base_name.replace(" ", "_") + "_upgrade"

        # Set the max level to 5
        max_level = 5

        # Check to see if the item is fully leveled
        def fully_leveled(item):
            return item == max_level

        # Returns a string to send as an error (taking in the upgrade before)
        def upgrade_error(msg_text):
            msg_text = msg_text.replace("_", " ").title()
            error_msg = f"The {msg_text} needs upgraded first!"
            return error_msg

        # If the upgrade is in tier 1 set the cost list used to the first one
        if upgrade in self.TIER_1:
            upgrade_cost_list_used = self.UPGRADE_COST_LIST

        # Else if its in tier 2...
        elif upgrade in self.TIER_2:

            # Find parent tier and check if it's upgraded
            parent = [key for key, val in self.TIER_1.items()
                      if upgrade in val][0]
            if not fully_leveled(upgrades[parent]):
                return await ctx.send(upgrade_error(parent))

            # Set the cost list used to the second one
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_TWO

        # Else if its in tier 3
        elif upgrade in self.TIER_3:

            # Find parent tier and check if it's upgraded
            parent = [key for key, val in self.TIER_2.items()
                      if upgrade in val][0]
            if not fully_leveled(upgrades[parent]):
                return await ctx.send(upgrade_error(parent))

            # Set the cost list used to the third one
            upgrade_cost_list_used = self.UPGRADE_COST_LIST_THREE

        # Else tell them it's not valid
        else:
            return await ctx.send("That's not a valid upgrade.")

        # Check level of validated upgrade
        upgrade_level = upgrades[upgrade]
        if fully_leveled(upgrade_level):
            return await ctx.send("That upgrade is fully upgraded.")

        # if they dont have enough money tel them that
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

        # And send the bought level with the name for the cost
        await ctx.send(
            f"You bought the Level {upgrade_level + 1} "
            f"{upgrade_base_name.title()} Upgrade for "
            f"{upgrade_cost_list_used[upgrade_level]:,}!"
        )


def setup(bot):
    """Bot Setup"""
    bot.add_cog(Upgrades(bot))
