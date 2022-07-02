from ntpath import join
import random
import math
import asyncio
from PIL.Image import new
import discord
from datetime import datetime as dt, timedelta
from discord.ext import commands, tasks, vbu
import string

from cogs import utils
from cogs.utils import EMOJIS
from cogs.utils.fish_handler import FishSpecies


class Fishing(vbu.Cog):
    cast_time = dt.utcnow()
    # Start the loop when the cog is started

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.user_cast_loop.start()

    # When the cog is turned off, turn the loop off
    def cog_unload(self):
        self.user_cast_loop.cancel()

    # Every hour, everyone gets a cast as long as they have less than 50
    @tasks.loop(hours=1)
    async def user_cast_loop(self):
        self.cast_time = dt.utcnow()
        async with vbu.Database() as db:
            casts = await db("""SELECT * FROM user_balance""")
            for x in casts:
                if x["casts"] >= 50:
                    continue
                amount_of_crafted = await utils.user_item_inventory_db_call(
                    x["user_id"])
                if amount_of_crafted:
                    if amount_of_crafted[0]['fishing_boots'] <= 5:
                        boot_multiplier = amount_of_crafted[0]['fishing_boots']
                    else:
                        boot_multiplier = 5
                else:
                    boot_multiplier = 0
                amount = random.choices(
                    [1, 2], [(1 - (.04 * boot_multiplier)), (.04 * boot_multiplier)])[0]
                await db(
                    """UPDATE user_balance SET casts=casts+$2 WHERE user_id = $1""",
                    x["user_id"], amount
                )

    # Wait until the bot is on and ready and not just until the cog is on
    @user_cast_loop.before_loop
    async def before_user_cast_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        This command catches a fish.
        """

        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

        # Check to see if they've registered with the bot before
        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")

        # Fetch their upgrades and casts
        async with vbu.Database() as db:
            upgrades = await utils.user_upgrades_db_call(ctx.author.id)
            casts = await utils.user_balance_db_call(ctx.author.id)
            user_locations_info = await utils.user_location_info_db_call(
                ctx.author.id)
            user_inventory = await utils.user_fish_inventory_db_call(ctx.author.id)
            location_pools_info = await utils.fish_pool_location_db_call()

            if not user_locations_info:
                await db(
                    """INSERT INTO user_location_info (user_id, current_location) VALUES ($1, 'pond')"""
                )

        # If they have no casts tell them they can't fish and remove them from currrent fishers
        if casts[0]["casts"] <= 0:
            relative_time = discord.utils.format_dt(
                self.cast_time - timedelta(hours=(utils.DAYLIGHT_SAVINGS - 1)),
                style="R",
            )
            return await ctx.send(
                f"You have no casts, You will get another {relative_time}."
            )

        # pick a random number using the line upgrade, if it is equal to 1 they get to fish twice
        caught_fish = 1
        two_in_one_roll = random.randint(
            1, utils.LINE_UPGRADES[upgrades[0]["line_upgrade"]]
        )
        if two_in_one_roll == 1:
            caught_fish = 2

        # For each fish caught...
        for _ in range(caught_fish):

            # If they didn't catch trash
            if random.randint(1, 12) != 12:

                # Use upgrades for chances of rarity and mutation, and choose one with weighted randomness
                rarity = random.choices(
                    *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                )[0]
                while rarity not in FishSpecies.all_species_by_location_rarity[user_locations_info[0]['current_location']].keys():
                    rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                special = random.choices(("normal", "skinned"),
                                         (1-utils.LURE_UPGRADES[upgrades[0]["lure_upgrade"]],
                                          utils.LURE_UPGRADES[upgrades[0]["lure_upgrade"]])
                                         )[0]

                # See which fish they caught by taking a random fish from the chosen rarity)
                if ctx.author.id not in utils.user_last_fish_caught.keys():
                    utils.user_last_fish_caught[ctx.author.id] = ""
                chosen_fish = random.choice(
                    FishSpecies.get_location_rarity(
                        rarity, user_locations_info[0]['current_location'])
                )
                while chosen_fish.name in utils.past_fish or location_pools_info[0][f"{chosen_fish.name}_count"] <= 0 or chosen_fish.name == utils.user_last_fish_caught[ctx.author.id]:
                    rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                    chosen_fish = random.choice(
                        FishSpecies.get_location_rarity(
                            rarity, user_locations_info[0]['current_location'])
                    )

                utils.user_last_fish_caught[ctx.author.id] = chosen_fish.name
                # If the fish is skinned, choose one of it's skins
                fish_skin = ""
                if special == "skinned":
                    fish_skin = random.choice(chosen_fish.skins)

                # Grammar
                a_an = (
                    "an" if rarity[0].lower() in (
                        "a", "e", "i", "o", "u") else "a"
                )

                # Get their fish inventory, add 1 to their times caught in achievements, subtract 1 from their casts
                async with vbu.Database() as db:
                    await db(
                        f"""UPDATE user_location_info SET {chosen_fish.name}_caught = {chosen_fish.name}_caught + 1 WHERE user_id = $1""",
                        ctx.author.id,
                    )
                    # Achievements
                    await db(
                        """UPDATE user_achievements SET times_caught = times_caught + 1 WHERE user_id = $1""",
                        ctx.author.id,
                    )
                    await db(
                        """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                        ctx.author.id,
                    )
                    await db(
                        f"""UPDATE fish_pool_location SET {chosen_fish.name}_count = {chosen_fish.name}_count - 1"""
                    )

                # Find out how many of those fish they caught previously
                amount = user_locations_info[0][f"{chosen_fish.name}_caught"]

                # Set the fish file to the fishes image
                if fish_skin != "":
                    fish_file = discord.File(
                        f"{chosen_fish.image[:40]}{fish_skin}_{chosen_fish.image[40:]}", "new_fish.png")
                else:
                    fish_file = discord.File(chosen_fish.image, "new_fish.png")

                # Add the fish caught's name to the choices
                choices = [chosen_fish.name.replace('_', ' ').title()]

                # For three other fish...
                for _ in range(3):

                    # Get a random other fish
                    random_rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                    random_fish = random.choice(
                        utils.FishSpecies.get_rarity(random_rarity))

                    # If it's already a choice find a new one
                    while random_fish.name.replace('_', ' ').title() in choices:
                        random_rarity = random.choices(
                            *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                        )[0]
                        random_fish = random.choice(
                            utils.FishSpecies.get_rarity(random_rarity))

                    # Add that fish to the choices
                    choices.append(random_fish.name.replace('_', ' ').title())

                # Shuffle the choices so they're random
                random.shuffle(choices)

                # And send the choices as buttons
                components = discord.ui.MessageComponents(
                    discord.ui.ActionRow(
                        discord.ui.Button(
                            label=choices[0], custom_id=choices[0]
                        ),
                        discord.ui.Button(
                            label=choices[1], custom_id=choices[1]
                        ),
                        discord.ui.Button(
                            label=choices[2], custom_id=choices[2]
                        ),
                        discord.ui.Button(
                            label=choices[3], custom_id=choices[3]
                        ),
                    ),
                )

                # Sends the message with the pic of fish and buttons
                guess_message = await ctx.send(f"{EMOJIS['aqua_shrug']}Guess The Species:", file=fish_file, components=components)

                # Make the button check
                def button_check(payload):
                    if payload.message.id != guess_message.id:
                        return False
                    self.bot.loop.create_task(payload.response.defer_update())
                    return payload.user.id == ctx.author.id

                # Wait for them to click a button
                try:
                    chosen_button_payload = await self.bot.wait_for(
                        "component_interaction", timeout=60.0, check=button_check
                    )
                    chosen_button = (
                        chosen_button_payload.component.custom_id
                    )
                    await guess_message.edit(
                        components=None
                    )
                except asyncio.TimeoutError:
                    await guess_message.edit(
                        components=None
                    )
                    await ctx.send("Timed out asking for guess...")
                    chosen_button = "AAAAAAAAAAAAAA"

                # Give them a bonus based on the fish's cost and tell them they got it correct if they did
                if chosen_button == chosen_fish.name.replace('_', ' ').title():
                    bonus = 15 + math.floor(int(chosen_fish.cost) / 10)
                    guess_message = f"{EMOJIS['aqua_love']} <@{ctx.author.id}> guessed correctly and recieved a bonus of {bonus} {EMOJIS['sand_dollar']}!"

                    # Update the users balance with the bonus
                    async with vbu.Database() as db:
                        await db(
                            """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
                            ctx.author.id,
                            bonus,
                        )

                # Else tell them it was wrong
                else:
                    guess_message = f"{EMOJIS['aqua_pensive']} Incorrect <@{ctx.author.id}>, no bonus given."

                # Tell the user about the fish they caught
                owned_unowned = "Owned" if amount > 0 else "Unowned"
                if fish_skin != "":
                    fish_skin_underlined = f"__{fish_skin}__"
                else:
                    fish_skin_underlined = ""
                embed = discord.Embed(
                    title=f"{EMOJIS['aqua_fish']} {ctx.author.display_name} caught {a_an} *{rarity}* {fish_skin_underlined} {chosen_fish.size} **{chosen_fish.name.replace('_', ' ').title()}**!"
                )
                embed.add_field(
                    name=owned_unowned,
                    value=f"You have caught {amount} **{chosen_fish.name.replace('_', ' ').title()}**",
                    inline=False,
                )
                embed.add_field(
                    name="** **", value=f"*{random.choice(utils.fish_footers)}*")
                embed.set_image(url="attachment://new_fish.png")
                embed.color = utils.RARITY_CULERS[rarity]
                if casts[0]["casts"] == 3:
                    guess_message += "\n⚠️You have two casts left⚠️"
                # Ask if they want to sell the fish they just caught or keep it

                await ctx.send(guess_message)
                await utils.ask_to_sell_fish(self.bot, ctx, chosen_fish, fish_skin, embed=embed)

                # Find if they catch a crate with the crate_chance_upgrade
                crate_catch = random.randint(
                    1, utils.CRATE_CHANCE_UPGRADE[upgrades[0]
                                                  ["crate_chance_upgrade"]]
                )

                # If they caught it...
                if crate_catch == 1:
                    crate_loot = []

                    # Choose a random crate tier based on their crate_tier_upgrade and add the loot for that tier
                    crate = random.choices(
                        (
                            "Wooden",
                            "Bronze",
                            "Steel",
                            "Golden",
                            "Diamond",
                            "Enchanted",
                        ),
                        utils.CRATE_TIER_UPGRADE[upgrades[0]
                                                 ["crate_tier_upgrade"]],
                    )
                    crate_loot.append(
                        (
                            "balance",
                            random.randint(0, utils.CRATE_TIERS[crate[0]][0]),
                            "user_balance",
                        )
                    )
                    crate_loot.append(
                        (
                            "casts",
                            random.randint(0, utils.CRATE_TIERS[crate[0]][1]),
                            "user_balance",
                        )
                    )
                    crate_loot.append(
                        (
                            random.choices(
                                ("none", "cfb", "ufb", "rfb", "ifb", "hlfb"),
                                utils.CRATE_TIERS[crate[0]][2],
                            )[0],
                            random.randint(0, utils.CRATE_TIERS[crate[0]][3]),
                            "user_inventory",
                        )
                    )
                    crate_loot.append(
                        (
                            random.choices(
                                ("none", "flakes", "pellets", "wafers"),
                                utils.CRATE_TIERS[crate[0]][4],
                            )[0],
                            random.randint(0, utils.CRATE_TIERS[crate[0]][5]),
                            "user_inventory",
                        )
                    )
                    crate_loot.append(
                        (
                            random.choices(
                                ("none", "fullness", "experience", "mutation"),
                                utils.CRATE_TIERS[crate[0]][6],
                            )[0],
                            random.randint(0, utils.CRATE_TIERS[crate[0]][7]),
                            "user_inventory",
                        )
                    )

                    # Initialize variables and display variable for every item
                    crate_message = ""
                    nl = "\n"
                    display = {
                        "balance": "Sand Dollars",
                        "casts": "Casts",
                        "cfb": "Common Fish Bags",
                        "ufb": "Uncommon Fish Bags",
                        "rfb": "Rare Fish Bags",
                        "ifb": "Inverted Fish Bags",
                        "hlfb": "High Level Fish Bags",
                        "flakes": "Fish Flakes",
                        "pellets": "Fish Pellets",
                        "wafers": "Fish Wafers",
                        "experience": "Experience Potions",
                        "mutation": "Mutation Potions",
                        "fullness": "Fullness Potions",
                    }

                    async with vbu.Database() as db:
                        # For each piece of loot in the crate
                        for data in crate_loot:

                            # Unpack the data
                            type_of_loot, amount_of_loot, table_of_loot = data
                            # If the type isn't "none" and there is an amount insert the loot into their database
                            if type_of_loot != "none" and amount_of_loot != 0:
                                await db(
                                    """UPDATE {0} SET {1} = {1} + $2 WHERE user_id = $1""".format(
                                        table_of_loot, type_of_loot
                                    ),
                                    ctx.author.id,
                                    amount_of_loot,
                                )
                                # Add a message to the end of the string to be sent
                                crate_message += f"{nl}{amount_of_loot}x {display[type_of_loot]} recieved!"

                        # Send the message telling them they caught a crate and what was in it
                        await ctx.channel.send(
                            f"{ctx.author.display_name} caught a {crate[0]} crate containing: {crate_message}"
                        )

            # Else if they catch trash...
            else:

                # Still use up a cast
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                        ctx.author.id,
                    )

                # Initiate the trash dict and string
                trash_dict = {}
                trash_string = ""

                # For each trash caught (1-6)...
                for i in range(random.randint(1, 6)):

                    # They catch a random weighted trash
                    caught = random.choices(
                        (
                            "Pile Of Bottle Caps",
                            "Plastic Bottle",
                            "Plastic Bag",
                            "Seaweed Scraps",
                            "Broken Fishing Net",
                            "Halfeaten Flip Flop",
                            "Pile Of Straws",
                            "Old Boot",
                            "Old Tire"
                        ),
                        (
                            .15,
                            .15,
                            .15,
                            .15,
                            .1,
                            .1,
                            .1,
                            .05,
                            .05,
                        )
                    )[0]

                    # If its not already in the dict add it with a 1, else add 1 to it
                    if caught not in trash_dict.keys():
                        trash_dict[caught] = 1
                    else:
                        trash_dict[caught] += 1

                # for each type of trash...
                for trash, amount in trash_dict.items():

                    # Add that trash to a string
                    trash_string += "\n" + \
                        f"{utils.EMOJIS[trash.replace(' ', '_').lower()]}{trash}: {amount}"

                    # Add the trash to their inventory
                    async with vbu.Database() as db:
                        await db(
                            f"""UPDATE user_item_inventory SET {trash.replace(' ', '_').lower()} = {trash.replace(' ', '_').lower()}+ {amount} WHERE user_id = $1""",
                            ctx.author.id,
                        )

                # Tell them they caught trash and how much of what types
                await ctx.send(f"{EMOJIS['aqua_trash']} You caught trash!{trash_string}")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        This command renames a specified fish or tank.
        """

        # Get the user's fish with the old name, all their fish, and all their tanks
        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""",
                old,
                ctx.author.id,
            )
            tank_rows = await utils.user_tank_inventory_db_call(ctx.author.id)
            fish_rows = await utils.user_fish_inventory_db_call(ctx.author.id)
        # Finds if you're renaming a tank
        spot_of_old = None
        if tank_rows:

            # If the old name is in tank rows, find the spot of it
            if old in tank_rows[0]["tank_name"]:
                for spot, tank in enumerate(tank_rows[0]["tank_name"]):
                    if old == tank:
                        spot_of_old = spot + 1

                    # If the new name matches any tanks return that they have a tank with that name
                    if new == tank:
                        return await ctx.send(
                            f"You already have a tank named **{new}**!",
                            allowed_mentions=discord.AllowedMentions.none(),
                        )

                # rename the tank in the database and make any fish in that tank in the new named tank
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_tank_inventory SET tank_name[$3]=$1 WHERE user_id=$2;""",
                        new,
                        ctx.author.id,
                        spot_of_old,
                    )
                    await db(
                        """UPDATE user_fish_inventory SET tank_fish=$1 WHERE user_id = $2 AND tank_fish=$3""",
                        new,
                        ctx.author.id,
                        old,
                    )

                # Send confirmation message
                return await ctx.send(
                    f"{EMOJIS['aqua_love']}Congratulations, you have renamed **{old}** to **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Tell them if there is no fish or tank with the old name
        if not spot_of_old:
            if not fish_row:
                return await ctx.send(
                    f"{EMOJIS['aqua_shrug']}You have no fish or tank named **{old}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Check of fish is being changed to a name of a new fish
        for fish_name in fish_rows:
            if new == fish_name:
                return await ctx.send(
                    f"{EMOJIS['aqua_shrug']}You already have a fish named **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Update the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET fish_name=$1 WHERE user_id=$2 and fish_name=$3;""",
                new,
                ctx.author.id,
                old,
            )

        # Send confirmation message
        await ctx.send(
            f"{EMOJIS['aqua_love']}Congratulations, you have renamed **{old}** to **{new}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def craft(self, ctx: commands.Context, *, crafted: str = None):
        '''
        Crafts inputted item, gives a list of what to craft and what it costs if not
        '''

        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")
        # Let them enter the lowercase of the item if they want to
        if crafted:
            crafted = crafted.title()

        # Set up the menu for what is craftable and how much they cost
        crafting_menu_message = ""
        for craftable, needed in utils.items_required.items():
            crafting_menu_message += f"\n**{craftable}**"
            for item, amount in needed[0].items():
                crafting_menu_message += f"\n{utils.EMOJIS['bar_empty']}{item.replace('_', ' ').title()}: {amount}"
            crafting_menu_message += f"\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}{needed[1]}"
        crafting_menu_message += "\n*Specify what you want to craft with* `craft Item Name`"

        # If they don't enter a craftable item or don't enter anything give the craftable menu
        if not crafted or crafted not in utils.items_required.keys():
            return await ctx.send(crafting_menu_message)

        # If they enter one of the stacking items, check that they don't have the max
        if crafted in ["Fishing Boots", "Trash Toys"]:
            async with vbu.Database() as db:
                amount_of_crafted = await db(f"""SELECT {crafted.replace(' ', '_').lower()} FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
            if amount_of_crafted[0][crafted.replace(' ', '_').lower()] == 5:
                return await ctx.send("You have the max amount of this item!")

        # If they don't have the items to craft, let them know
        if not await utils.enough_to_craft(crafted, ctx.author.id):
            return await ctx.send("You do not have the required items to craft this.")

        async with vbu.Database() as db:

            # Get rid of the items taken to craft
            for item, required in utils.items_required[crafted][0].items():
                await db(f"""UPDATE user_item_inventory SET {item} = {item} - {required} WHERE user_id = $1""", ctx.author.id)

            # If its a fish bag pick a random bag to craft, else use crafted for the db
            if crafted == "Fish Bag":
                db_crafted = random.choice(["cfb", "ufb", "rfb"])
                if db_crafted.title() in utils.COMMON_BAG_NAMES:
                    crafted = utils.COMMON_BAG_NAMES[0]
                elif db_crafted.title() in utils.UNCOMMON_BAG_NAMES:
                    crafted = utils.UNCOMMON_BAG_NAMES[0]
                elif db_crafted.title() in utils.RARE_BAG_NAMES:
                    crafted = utils.RARE_BAG_NAMES[0]
            else:
                db_crafted = crafted.replace(" ", "_").lower()

            # If they get a cast go to the user_balance table, else use the item inventory, and add 1 to the amount
            if db_crafted == "cast":
                await db(f"""UPDATE user_balance SET casts = casts + 1 WHERE user_id = $1""", ctx.author.id)
            else:
                await db(f"""UPDATE user_item_inventory SET {db_crafted} = {db_crafted} + 1 WHERE user_id = $1""", ctx.author.id)

        # Let them know it was crafted
        return await ctx.send(f"{crafted} has been crafted!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def map(self, ctx: commands.Context):
        locations = ["Pond", "Creek", "Estuary", "Coral Reef",
                     "Ocean", "Deep Sea", "River", "Lake"]

        map = discord.File(
            "C:/Users/JT/Pictures/Aqua/assets/images/background/World Map.png", "mapfile.png")
        await ctx.send(file=map)
        location = await utils.create_select_menu(
            self.bot, ctx, locations, "location", "choose", True
        )
        if location in locations:
            location = location.replace(' ', '_').lower()
            async with vbu.Database() as db:
                user_fish_caught = await utils.user_location_info_db_call(ctx.author.id)
                fish_pool_left = await utils.fish_pool_location_db_call()
                user_inventory = await utils.user_item_inventory_db_call(ctx.author.id)
            embed = discord.Embed(
                title=f"{location.replace('_', ' ').title()} Info")
            for rarity, fish in FishSpecies.all_species_by_location_rarity[location].items():
                rarity = rarity.upper()
                fish_in_rarity = []
                for single_fish in fish:
                    if user_fish_caught[0][f"{single_fish.name}_caught"] > 0:
                        fish_in_rarity.append(
                            f"{single_fish.name.replace('_', ' ').title()} ({fish_pool_left[0][f'{single_fish.name}_count']} Left)")
                    else:
                        fish_in_rarity.append(
                            f"??? ({fish_pool_left[0][f'{single_fish.name}_count']} Left)\t")
                embed.add_field(name=rarity, value='\n'.join(
                    [f"{fish}" for fish in fish_in_rarity]), inline=True)
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(custom_id="choose", label="Travel Here"),
                    discord.ui.Button(custom_id="unlock",
                                      label="Unlock This Location")
                ),
            )
            embed.color = 0x4AFBEF
            components.get_component("unlock").disable()
            if location in ["coral_reef", "ocean", "deep_sea", "river", "lake"]:
                embed.color = 0xFFE80D
                components.get_component("choose").disable()
                if not user_fish_caught[0][f'{location}_unlocked']:
                    if user_inventory[0]['new_location_unlock'] > 0:
                        components.get_component("unlock").enable()
                else:
                    components.get_component("choose").enable()
            message = await ctx.send(embed=embed, components=components)

            def button_check(payload):
                if payload.message.id != message.id:
                    return False
                return payload.user.id == ctx.author.id

            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
                if chosen_button_payload.component.custom_id == 'choose':
                    await ctx.send(f"traveled to {location.replace('_', ' ').title()}")
                    await chosen_button_payload.response.defer_update()
                    async with vbu.Database() as db:
                        if not user_fish_caught:
                            await db("""INSERT INTO user_location_info (user_id) VALUES ($1)""", ctx.author.id)
                        await db("""UPDATE user_location_info SET current_location = $2 WHERE user_id = $1""", ctx.author.id, location)
                elif chosen_button_payload.component.custom_id == 'unlock':
                    await chosen_button_payload.response.defer_update()
                    async with vbu.Database() as db:
                        await db("""UPDATE user_item_inventory SET new_location_unlock = new_location_unlock - 1 WHERE user_id = $1""", ctx.author.id)
                        await db(f"""UPDATE user_location_info SET {location}_unlocked = TRUE WHERE User_id = $1""", ctx.author.id)
                await message.edit(components=components.disable_components())
            except asyncio.TimeoutError:
                await message.edit(components=components.disable_components())

# test


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
