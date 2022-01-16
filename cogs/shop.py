import random
import asyncio
from datetime import datetime as dt, timedelta

import textwrap
import discord
from discord.ext import commands
import voxelbotutils as vbu

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS
from cogs.utils.misc_utils import create_bucket_embed
from cogs.utils import EMOJIS

# Set up the fields for the shop
SHOP_FIELDS = [
    (
        "Fish Shop\n*These are neutral items for sale.*",
        f"**Fish Points {EMOJIS['fish_points']}** __Price: 500 {EMOJIS['sand_dollar']}__\n"
        f"One permanant point for the \"Fish Points\" leaderboard\n"
        f"**Fishing Casts {EMOJIS['casts']}** __Price: 5 {EMOJIS['doubloon']}__\n"
        f"Five casts to be used for fishing\n"
        f"**Sand Dollars {EMOJIS['sand_dollar']}** __Price: 1 {EMOJIS['doubloon']}__\n"
        f"1,500 sand dollars to spend on various goods\n"
        f"**Fish Revival {EMOJIS['revival']}** __Price: 2,500 {EMOJIS['sand_dollar']}__\n"
        f"Fish revival to bring your fish back to life after it has died\n"
        f"**Plant Life** __Price: 250 {EMOJIS['doubloon']}__\n"
        f"The plant life theme for one of your tanks\n"
    ),
    (
        f"{EMOJIS['amfc']} __AquaMarine Fish Corps State Issued Resources__ {EMOJIS['amfc']}\n"
        f"These are resources bought from the AMFC company.",
        f"**Fish Flakes {EMOJIS['fish_flake']}** __Price: 200 {EMOJIS['sand_dollar']}__\n"
        f"Fish flakes to feed a fish that is level 1-20, keeping them alive \n"
        f"**Fish Pellets {EMOJIS['fish_pellet']}** __Price: 500 {EMOJIS['sand_dollar']}__\n"
        f"Fish pellets to feed a fish that is level 21-50, keeping them alive \n"
        f"**Fish Wafers {EMOJIS['fish_wafer']}** __Price: 1000 {EMOJIS['sand_dollar']}__\n"
        f"Fish wafers to feed a fish that is level 51+, keeping them alive \n"
        f"**Fish Bowl** __Price: 500 {EMOJIS['sand_dollar']}__\n"
        f"Fish Bowl Tank that you can deposit one small fish into \n"
        f"**Small Tank** __Price: 2,000 {EMOJIS['sand_dollar']}__\n"
        f"Small Tank that you can deposit five small fish or one medium fish into\n"
        f"**Medium Tank** __Price: 12,000 {EMOJIS['sand_dollar']}__\n"
        f"Medium Tank that you can deposit twenty five small fish, five medium fish, or one large fish into \n"
    ),
    (
        f"{EMOJIS['gfu']} __Golden Fishers Union Item Market__ {EMOJIS['gfu']}\n"
        f"These are items sold by the GFU",
        f"**Common Fish Bag {EMOJIS['common_fish_bag']}** __Price: 50 {EMOJIS['sand_dollar']}__\n"
        f"One fish from the common rarity \n"
        f"**Uncommon Fish Bag {EMOJIS['uncommon_fish_bag']}** __Price: 150 {EMOJIS['sand_dollar']}__\n"
        f"One fish from the uncommon rarity \n"
        f"**Rare Fish Bag {EMOJIS['rare_fish_bag']}** __Price: 750 {EMOJIS['sand_dollar']}__\n"
        f"One fish from the rare rarity \n"
        f"**Inverted Fish Bag {EMOJIS['inverted_fish_bag']}** __Price: 100,000 {EMOJIS['sand_dollar']}__\n"
        f"One inverted fish from any rarity \n"
        f"**High Level Fish Bag {EMOJIS['high_level_fish_bag']}** __Price: 75,000 {EMOJIS['sand_dollar']}__\n"
        f"One fish from any rarity between the levels 10-50 \n"
        f"**Feeding Potion {EMOJIS['feeding_potion']}** __Price; 10,000 {EMOJIS['sand_dollar']}__\n"
        f"Feeding potion that will make your fish full for 30 days \n"
        f"**Experience Potion {EMOJIS['experience_potion']}** __Price: 40,000 {EMOJIS['sand_dollar']}__\n"
        f"Experience potion that gives your fish 10,000 experience \n"
        f"**Mutation Potion {EMOJIS['mutation_potion']}** __ Price: 50 {EMOJIS['doubloon']}__\n"
        f"Mutation potion that turns one of your fish inverted \n"
    ),
]


class Shop(vbu.Cog):
    @commands.command(aliases=["s", "store"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        This command shows everything buyable in the shop, along with their prices.
        """

        # Check the size of the fields and make sure they're correct
        fields = []
        for field in SHOP_FIELDS:
            [fields.append(i) for i in utils.get_fixed_field(field)]

        # Send the correct fields paginated
        await utils.paginate(ctx, fields, ctx.author)

    @commands.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """
        This command buys an item from a shop with the given amount.
        """

        # All the valid names
        all_names = [
            utils.COMMON_BAG_NAMES,
            utils.UNCOMMON_BAG_NAMES,
            utils.RARE_BAG_NAMES,
            utils.FISH_FLAKES_NAMES,
            utils.FISH_BOWL_NAMES,
            utils.SMALL_TANK_NAMES,
            utils.MEDIUM_TANK_NAMES,
            utils.PLANT_LIFE_NAMES,
            utils.FISH_REVIVAL_NAMES,
            utils.CASTS_NAMES,
            utils.SAND_DOLLAR_NAMES,
            utils.FISH_PELLETS_NAMES,
            utils.FISH_WAFERS_NAMES,
            utils.FISH_POINTS_NAMES,
            utils.EXPERIENCE_POTION_NAMES,
            utils.MUTATION_POTION_NAMES,
            utils.FEEDING_POTION_NAMES,
            utils.INVERTED_BAG_NAMES,
            utils.HIGH_LEVEL_BAG_NAMES,
        ]

        # See if they gave a valid item
        if not any([item.title() in name_list for name_list in all_names]):
            return await ctx.send("That is not an available item")

        # Set up SQL statements for each of the tiered inserts
        inventory_insert_sql = (
            "INSERT INTO user_item_inventory (user_id, {0}) VALUES ($1, $2) ON CONFLICT "
            "(user_id) DO UPDATE SET {0}=user_item_inventory.{0}+excluded.{0}"
        )
        balance_insert_sql = (
            "INSERT INTO user_balance (user_id, {0}) VALUES ($1, $2) ON CONFLICT "
            "(user_id) DO UPDATE SET {0}=user_balance.{0}+excluded.{0}"
        )

        # Info for each item; {name: (accepted named, price, display name, sql statement)}
        item_name_dict = {
            "cfb": (
                utils.COMMON_BAG_NAMES,
                50,
                "Common Fish Bag",
                inventory_insert_sql.format("cfb"),
            ),
            "ufb": (
                utils.UNCOMMON_BAG_NAMES,
                150,
                "Uncommon Fish Bag",
                inventory_insert_sql.format("ufb"),
            ),
            "rfb": (
                utils.RARE_BAG_NAMES,
                750,
                "Rare Fish Bag",
                inventory_insert_sql.format("rfb"),
            ),
            "ifb": (
                utils.INVERTED_BAG_NAMES,
                100000,
                "Inverted Fish Bag",
                inventory_insert_sql.format("ifb"),
            ),
            "hlfb": (
                utils.HIGH_LEVEL_BAG_NAMES,
                75000,
                "High Level Fish Bag",
                inventory_insert_sql.format("hlfb"),
            ),
            "flakes": (
                utils.FISH_FLAKES_NAMES,
                200,
                "Fish Flakes",
                inventory_insert_sql.format("flakes"),
            ),
            "pellets": (
                utils.FISH_PELLETS_NAMES,
                500,
                "Fish Pellets",
                inventory_insert_sql.format("pellets"),
            ),
            "wafers": (
                utils.FISH_WAFERS_NAMES,
                1000,
                "Fish Wafers",
                inventory_insert_sql.format("wafers"),
            ),
            "revival": (
                utils.FISH_REVIVAL_NAMES,
                2500,
                "Fish Revival",
                inventory_insert_sql.format("revival"),
            ),
            "Fish Bowl": (utils.FISH_BOWL_NAMES, 500, "Fish Bowl", ""),
            "Small Tank": (utils.SMALL_TANK_NAMES, 2000, "Small Tank", ""),
            "Medium Tank": (utils.MEDIUM_TANK_NAMES, 12000, "Medium Tank", ""),
            "Plant Life": (utils.PLANT_LIFE_NAMES, 250, "Plant Life", ""),
            "Fish Points": (
                utils.FISH_POINTS_NAMES,
                500,
                "Fish Points",
                balance_insert_sql.format("extra_points"),
            ),
            "Casts": (
                utils.CASTS_NAMES,
                5,
                "Casts",
                balance_insert_sql.format("casts"),
            ),
            "Sand Dollars": (
                utils.SAND_DOLLAR_NAMES,
                1,
                "Sand Dollars",
                balance_insert_sql.format("balance"),
            ),
            "Experience Potion": (
                utils.EXPERIENCE_POTION_NAMES,
                40000,
                "Experience Potions",
                inventory_insert_sql.format("experience_potions"),
            ),
            "Mutation Potion": (
                utils.MUTATION_POTION_NAMES,
                100,
                "Mutation Potions",
                inventory_insert_sql.format("mutation_potions"),
            ),
            "Feeding Potion": (
                utils.FEEDING_POTION_NAMES,
                15000,
                "Feeding Potions",
                inventory_insert_sql.format("feeding_potions"),
            ),
        }

        # All the items that you can only buy one of
        item_name_singular = (
            utils.FISH_BOWL_NAMES
            + utils.SMALL_TANK_NAMES
            + utils.MEDIUM_TANK_NAMES
            + utils.PLANT_LIFE_NAMES
        )

        # All the items that cost doubloons
        Doubloon_things = (
            utils.PLANT_LIFE_NAMES
            + utils.CASTS_NAMES
            + utils.SAND_DOLLAR_NAMES
            + utils.MUTATION_POTION_NAMES
        )

        # Work out which of the SQL statements to use
        for table, data in item_name_dict.items():
            possible_entries = data[0]
            if item.title() not in possible_entries:
                continue

            # Unpack the given information
            _, cost, response, db_call = data

            if item.title() in item_name_singular:
                amount = 1

            # else:
            #     components = discord.ui.MessageComponents.add_number_buttons(
            #         add_negative=True)
            #     message = await ctx.send("How many of that item do you want to buy?", components=components)

            #     def button_check(payload):
            #         if payload.message.id != message.id:
            #             return False
            #         self.bot.loop.create_task(payload.response.defer_update())
            #         return payload.user.id == ctx.author.id
            #         # Keep going...

            # Figure out what type of balance to use
            type_of_balance = "balance"
            emoji = EMOJIS["sand_dollar"]
            if item.title() in Doubloon_things:
                emoji = EMOJIS["doubloon"]
                type_of_balance = "doubloon"

            # Find out the full cost
            full_cost = cost * amount

            # Find out how many are given for things that give more than one thing
            if response == "Casts":
                amount = amount * 5
            elif response == "Sand Dollars":
                amount = amount * 1500

            # Check if they have enough money
            if not await utils.check_price(
                self.bot, ctx.author.id, full_cost, type_of_balance
            ):
                return await ctx.send(
                    f"You don't have enough {emoji} for this!"
                )

            # Add item to user, check if item is a singular item and if so runs that function
            if item.title() in item_name_singular:
                if (
                    await utils.buying_singular(
                        self.bot, ctx.author, ctx, str(response)
                    )
                    is False
                ):
                    return
            else:
                async with vbu.Database() as db:
                    await db(db_call, ctx.author.id, amount)

        # Remove correct type of money from user
        if item.title() in Doubloon_things:
            async with vbu.Database() as db:
                await db(
                    """
                    UPDATE user_balance SET doubloon=doubloon-$1 WHERE user_id = $2""",
                    full_cost,
                    ctx.author.id,
                )
        else:
            async with vbu.Database() as db:
                await db(
                    """
                    UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""",
                    full_cost,
                    ctx.author.id,
                )

        # And tell the user we're done
        await ctx.send(
            f"You bought {amount:,} {response} for {full_cost:,} {emoji}!"
        )

    @commands.command(aliases=["u"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx: commands.Context, *, item: str):
        """
        This command is only for using fish bags, and is just like using the fish command.
        """

        # Don't let them use anything if they're fishing
        if ctx.author.id in utils.current_fishers:
            return await ctx.send(
                f"{ctx.author.display_name}, you're already fishing!"
            )

        # Set a bunch of variables up for bags
        rarity_of_bag = None
        used_bag = None
        used_bag_humanize = None
        type_of_bag = None

        # Based on the type of bag, unpack the variables
        if item.title() in utils.COMMON_BAG_NAMES:
            used_bag_humanize, rarity_of_bag, used_bag = utils.COMMON_BAG_NAMES
        elif item.title() in utils.UNCOMMON_BAG_NAMES:
            (
                used_bag_humanize,
                rarity_of_bag,
                used_bag,
            ) = utils.UNCOMMON_BAG_NAMES
        elif item.title() in utils.RARE_BAG_NAMES:
            used_bag_humanize, rarity_of_bag, used_bag = utils.RARE_BAG_NAMES
        elif item.title() in utils.INVERTED_BAG_NAMES:
            used_bag_humanize, type_of_bag, used_bag = utils.INVERTED_BAG_NAMES
        elif item.title() in utils.HIGH_LEVEL_BAG_NAMES:
            (
                used_bag_humanize,
                type_of_bag,
                used_bag,
            ) = utils.HIGH_LEVEL_BAG_NAMES

        # Else if they want to use a potion
        elif item.title() in (
            utils.EXPERIENCE_POTION_NAMES
            + utils.MUTATION_POTION_NAMES
            + utils.FEEDING_POTION_NAMES
        ):

            # Figure out the type of potion used
            if item.title() in utils.EXPERIENCE_POTION_NAMES:
                type_of_potion = "experience_potions"
            elif item.title() in utils.MUTATION_POTION_NAMES:
                type_of_potion = "mutation_potions"
            elif item.title() in utils.FEEDING_POTION_NAMES:
                type_of_potion = "feeding_potions"

            # Get their items from database
            async with vbu.Database() as db:
                inventory_rows = await db(
                    """SELECT * FROM user_item_inventory WHERE user_id = $1""",
                    ctx.author.id,
                )

                # If they don't have any potions tell them that
                if (
                    not inventory_rows
                    or inventory_rows[0][type_of_potion] == 0
                ):
                    return await ctx.send("You have no potions of that type!")

            # Let them tell you what fish they want to give the potion to
            message = await ctx.send(
                "Enter the name of the fish you want to give that potion to."
            )

            # Check for the message the user sends
            def check(m):
                return m.author == ctx.author and m.channel == message.channel

            # Set the name to what the user enters
            try:
                name_message = await self.bot.wait_for(
                    "message", timeout=60.0, check=check
                )
                name = name_message.content

            # Timeout check
            except asyncio.TimeoutError:
                return await message.channel.send(
                    "Timed out asking for fish name"
                )

            # Find the fish with that name
            async with vbu.Database() as db:
                fish_row = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                    ctx.author.id,
                    name,
                )

            # Check for if the fish exists
            if not fish_row:
                return await ctx.send("There is no fish with that name.")

            # Remove one potion from the user
            async with vbu.Database() as db:
                await db(
                    f"""UPDATE user_item_inventory SET {type_of_potion} = {type_of_potion} - 1 Where user_id = $1""",
                    ctx.author.id,
                )

            # If they use an experience potion...
            if item.title() in utils.EXPERIENCE_POTION_NAMES:

                # Add 10k xp to the fish
                await utils.xp_finder_adder(ctx.author, name, 10000, False)\

                # Get the new rows
                async with vbu.Database() as db:
                    new_fish_rows = await db(
                        """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                        ctx.author.id,
                        name,
                    )

                # Let them know the new info of their fish
                return await ctx.send(
                    f"{new_fish_rows[0]['fish_name']} is now level {new_fish_rows[0]['fish_level']}, {new_fish_rows[0]['fish_xp']}/{new_fish_rows[0]['fish_xp_max']}"
                )

            # If they bought a mutation potion...
            if item.title() in utils.MUTATION_POTION_NAMES:

                # Add inverted to the fish type and update the database
                async with vbu.Database() as db:
                    mutated = "inverted_" + fish_row[0]["fish"]
                    await db(
                        """UPDATE user_fish_inventory SET fish = $1 where user_id = $2 AND fish = $3""",
                        mutated,
                        ctx.author.id,
                        fish_row[0]["fish"],
                    )

                    # Let them know it worked
                    return await ctx.send(
                        f"{fish_row[0]['fish_name']} looks kind of strange now..."
                    )

            # If the item is a feeding potion...
            if item.title() in utils.FEEDING_POTION_NAMES:

                # Set the time to be now + the new death date
                death_date = fish_row[0]["death_time"] + timedelta(
                    days=30, hours=0
                )

                # Update the fish's death date
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                        ctx.author.id,
                        fish_row[0]["fish_name"],
                        death_date,
                        dt.utcnow(),
                    )

                # Let them know the potion worked
                return await ctx.send("That fish feels strangely full now...")

        # Add them to current fishers so they can't fish
        utils.current_fishers.append(ctx.author.id)

        # Deal with bag usage
        if used_bag is not None:

            # If its a bag with rarity just lower it, else pick a random rarity
            if rarity_of_bag:
                rarity_of_bag = rarity_of_bag.lower()
            else:
                rarity_of_bag = random.choices(
                    *utils.rarity_percentage_finder(0)
                )[0]

            # Lower the used bag
            used_bag = used_bag.lower()

            # Find the users items
            async with vbu.Database() as db:
                user_rows = await db(
                    """SELECT * FROM user_item_inventory WHERE user_id=$1""",
                    ctx.author.id,
                )

                # Find how many bags of that type they have
                user_bag_count = user_rows[0][used_bag]

            # If they have none tell them they have no bags and remove them from current fishers
            if not user_bag_count:
                utils.current_fishers.remove(ctx.author.id)
                return await ctx.send(f"You have no {used_bag_humanize}s!")

            # Get them a fish
            new_fish = random.choice(
                list(self.bot.fish[rarity_of_bag].values())
            ).copy()

            # If it's one of the past fish rechoose
            while new_fish["raw_name"] in utils.past_fish:
                new_fish = random.choice(
                    list(self.bot.fish[rarity_of_bag].values())
                ).copy()

            # If the bag is inverted invert the fish
            if type_of_bag == "Inverted":
                new_fish = utils.make_inverted(new_fish.copy())

            # Set the level to 0 and if its a high level bag set level to 10 - 50
            level = 0
            if type_of_bag == "High Level":
                level = random.randint(25, 50)

            # Remove the bag from their inventory
            async with vbu.Database() as db:
                await db(
                    f"""UPDATE user_item_inventory SET {used_bag}={used_bag}-1 WHERE user_id=$1""",
                    ctx.author.id,
                )

        # A fish bag wasn't used
        elif used_bag is None:
            utils.current_fishers.remove(ctx.author.id)
            return await ctx.send("That is not a usable item!")

        # Check a/an
        amount = 0
        owned_unowned = "Unowned"
        a_an = (
            "an"
            if rarity_of_bag[0].lower() in ("a", "e", "i", "o", "u")
            else "a"
        )

        # Get the users amount of fish
        async with vbu.Database() as db:
            user_inventory = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id=$1""",
                ctx.author.id,
            )

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                ctx.author.id,
            )

        # Find how many of that fish the user has
        for row in user_inventory:
            if row["fish"] == new_fish["raw_name"]:
                amount = amount + 1
                owned_unowned = "Owned"

        # Tell the user about the fish they rolled
        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity_of_bag} {new_fish['name']}!"
        embed.add_field(
            name=owned_unowned,
            value=f"You have {amount} {new_fish['name']}",
            inline=False,
        )
        embed.color = utils.RARITY_CULERS[rarity_of_bag]
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], "new_fish.png")

        # Ask the user if they want to sell the fish
        await ctx.send(file=fish_file)
        await utils.ask_to_sell_fish(
            self.bot, ctx, new_fish, embed=embed, level_inserted=level
        )

        # Remove them from current fishers
        utils.current_fishers.remove(ctx.author.id)

    @commands.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx: commands.Context):
        """
        Shows the user's item inventory.
        """

        # Get the users item inventory
        async with vbu.Database() as db:
            fetched = await db(
                """SELECT * FROM user_item_inventory WHERE user_id = $1""",
                ctx.author.id,
            )

        # If theres no inventory tell them they have no items
        if not fetched:
            return await ctx.send("You have no items in your inventory!")

        # list of tuples with the name and the name in the database
        items = [
            ("Common Fish Bag", "cfb"),
            ("High Level Fish Bag", "hlfb"),
            ("Uncommon Fish Bag", "ufb"),
            ("Inverted Fish Bag", "ifb"),
            ("Rare Fish Bag", "rfb"),
            ("Fish Flake", "flakes"),
            ("Fish Pellet", "pellets"),
            ("Mutation Potion", "mutation_potions"),
            ("Fish Wafer", "wafers"),
            ("Experience Potion", "experience_potions"),
            ("Revival", "revival"),
            ("Feeding Potion", "feeding_potions"),
            ("Pile Of Bottle Caps", "pile_of_bottle_caps"),
            ("Plastic Bottle", "plastic_bottle"),
            ("Plastic Bag", "plastic_bag"),
            ("Seaweed Scraps", "seaweed_scraps"),
            ("Broken Fishing Net", "broken_fishing_net"),
            ("Halfeaten Flip Flop", "halfeaten_flip_flop"),
            ("Pile Of Straws", "pile_of_straws"),
            ("Old Boot", "old_boot"),
            ("Old Tire", "old_tire"),
        ]

        # Create an embed
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory")

        # initialize list
        title_value = []

        # For each item...
        for name in items:

            # Find the emoji
            emoji = f"{'_'.join(name[0].split(' ')).lower()}"

            # If its a bag get rid of the fish part to make it fit better
            if "Bag" in name[0]:
                name = (name[0].replace(' Fish', ''), name[1])

            # If they have more than one of the item add an s
            if fetched[0][name[1]] > 1:
                name = (name[0]+'s', name[1])

            # add the emoji, name, and amount formatted to the title list
            title_value.append(
                f"{utils.EMOJIS[emoji]} {name[0]} : {fetched[0][name[1]]}")

            # If the lists length is 2 add the two strings in it as name and value and reset the list
            if len(title_value) == 2:
                embed.add_field(
                    name=title_value[0], value=title_value[1], inline=True
                )
                title_value = []

        # Send the embed
        await ctx.send(embed=embed)

    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(
        self, ctx: commands.Context, user: discord.Member = None
    ):
        """
        This command checks the user's balance or another user's balance.
        """

        async with vbu.Database() as db:

            # If they specified someone get that users balance
            if user:
                other_or_self = f"{user.display_name} has"
                fetched = await db(
                    """SELECT * FROM user_balance WHERE user_id = $1""",
                    user.id,
                )

            # Else get your own balance
            else:
                other_or_self = "You have"
                fetched = await db(
                    """SELECT * FROM user_balance WHERE user_id = $1""",
                    ctx.author.id,
                )

            # If theres none of each type of balance say no, otherwise say that balance
            if not fetched or not fetched[0]["balance"]:
                amount_one = "no"
            else:
                amount_one = f"{fetched[0]['balance']:,}"
            if not fetched or not fetched[0]["doubloon"]:
                amount_two = "no"
            else:
                amount_two = f"{fetched[0]['doubloon']:,}"
            if not fetched or not fetched[0]["casts"]:
                amount_three = "no"
            else:
                amount_three = f"{fetched[0]['casts']:,}"

        # Send the users balance
        await ctx.send(f"""{other_or_self} {amount_one} Sand Dollars {EMOJIS["sand_dollar"]}!\n{other_or_self} {amount_two} Doubloons {EMOJIS["doubloon"]}!\n{other_or_self} {amount_three} Casts {EMOJIS["casts"]}!""")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def sell(self, ctx: commands.Context, *, fish_sold: str):
        """
        This command sells the specified fish, and it must be out of a tank.
        """

        # Set the cost to 0
        cost = 0

        # Get the fish row for the fish specified
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id,
                fish_sold,
            )

        # Checks for if the fish exists and if its not in a tank
        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_sold}!")
        if fish_row[0]["tank_fish"]:
            return await ctx.send(
                "That fish is in a tank, please remove it to sell it."
            )

        # Gets rid of the dead fish and deletes it from the database
        if fish_row[0]["fish_alive"] is False:
            async with vbu.Database() as db:
                await db(
                    """DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""",
                    ctx.author.id,
                    fish_sold,
                )
            return await ctx.send(
                f"You have flushed your dead fish, {fish_sold} for 0 {EMOJIS['sand_dollar']}!"
            )

        # Gets the level multiplier
        multiplier = fish_row[0]["fish_level"] / 20

        # Finds what fish the specified fish is and...
        for rarity, fish_types in self.bot.fish.items():
            for fish_type, fish_info in fish_types.items():
                if fish_info["raw_name"] == utils.get_normal_name(
                    fish_row[0]["fish"]
                ):

                    # Find the cost of the fish
                    cost = int(fish_info["cost"])

        # Get the sell money using the level multiplier
        sell_money = int(cost * (1 + multiplier))

        # Add the money to their balance
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id,
                sell_money,
            )

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + $2""",
                ctx.author.id,
                sell_money,
            )

            # Remove the fish from their inventory
            await db(
                """DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""",
                ctx.author.id,
                fish_sold,
            )

        # Tell them who they sold and how much they sold them for
        await ctx.send(
            f"You have sold {fish_sold} for {sell_money} {EMOJIS['sand_dollar']}!"
        )

    @commands.command(aliases=["d"])
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def daily(self, ctx: commands.Context):
        """
        This command gives the user a daily reward of 1000 Sand Dollars.
        """

        # Check if they voted and if not tell them they need to vote
        if await utils.get_user_voted(self.bot, ctx.author.id) is False:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "Please vote and then run this command to get the daily reward!"
            )

        # Adds the money to the users balance
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, 1000)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 1000""",
                ctx.author.id,
            )
            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, 1000)
                ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + 1000""",
                ctx.author.id,
            )

        # confirmation message
        return await ctx.send(
            f"Daily reward of 1,000 {EMOJIS['sand_dollar']} claimed!"
        )

    @daily.error
    async def daily_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R"
        )
        await ctx.send(
            f"Daily reward claimed, please try again {relative_time}."
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def gamble(self, ctx: commands.Context, amount: int):
        """
        This command gambles sand dollars for more sand dollars
        """

        # See if the user has enough money and enters a correct amount
        if amount % 100 != 0:
            return await ctx.send("Please enter an amount divisible by 100")

        if not await utils.check_price(self.bot, ctx.author.id, amount, "balance"):
            return await ctx.send(
                f"You don't have enough sand dollars for this! ({amount})"
            )

        async with vbu.Database() as db:
            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_gambled) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_gambled = user_achievements.times_gambled + 1""",
                ctx.author.id,
            )
            # Remove money from the user
            await db(
                """UPDATE user_balance SET balance=balance-$2 WHERE user_id = $1""",
                ctx.author.id, amount
            )

        # Set up some vars for later
        item_values = []  # The list of values that they rolled
        emoji_id = []  # The list of emojis that they rolled
        emojis = [EMOJIS["roll"]] * 3
        picked_buttons = [False] * 3

        # Pick three fish names from their rarity
        for i in range(3):
            item_values.append(
                random.randint(1, 31)
            )

        # Get the emojis for the values they rolled
        for value in item_values:
            if value <= 16:
                emoji_id.append(EMOJIS["sand_dollar"])
                type_of_balance = "balance"
                amount_won = amount * 3
                emoji = EMOJIS["sand_dollar"]
            elif value <= 24:
                emoji_id.append(EMOJIS["sand_dollar_pile"])
                type_of_balance = "balance"
                amount_won = amount * 6
                emoji = EMOJIS["sand_dollar"]
            elif value <= 28:
                emoji_id.append(EMOJIS["sand_dollar_stack"])
                type_of_balance = "balance"
                amount_won = amount * 12
                emoji = EMOJIS["sand_dollar"]
            elif value <= 30:
                emoji_id.append(EMOJIS["fish_points"])
                type_of_balance = "extra_points"
                amount_won = amount / 20
                emoji = EMOJIS["fish_points"]
            elif value <= 31:
                emoji_id.append(EMOJIS["doubloon"])
                type_of_balance = "doubloon"
                amount_won = amount / 100
                emoji = EMOJIS["doubloon"]

        # Create embed with the emojis
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s roll")
        embed.add_field(
            name="Click the buttons to stop the rolls!", value="".join(emojis)
        )

        # Create the components for the buttons
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    emoji="1\N{COMBINING ENCLOSING KEYCAP}", custom_id="one"
                ),
                discord.ui.Button(
                    emoji="2\N{COMBINING ENCLOSING KEYCAP}", custom_id="two"
                ),
                discord.ui.Button(
                    emoji="3\N{COMBINING ENCLOSING KEYCAP}", custom_id="three"
                ),
            ),
        )

        # Send the embed and buttons
        gamble_message = await ctx.send(embed=embed, components=components)

        # Make the button check
        def button_check(payload):
            if payload.message.id != gamble_message.id:
                return False
            self.bot.loop.create_task(payload.response.defer_update())
            return payload.user.id == ctx.author.id

        # Keep going...
        while True:

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
                chosen_button = (
                    chosen_button_payload.component.custom_id.lower()
                )
            except asyncio.TimeoutError:
                await gamble_message.edit(
                    components=components.disable_components()
                )
                break

            # Update the displayed emoji
            if chosen_button == "one" and picked_buttons[0] is False:
                emojis[0] = emoji_id[0]
                picked_buttons[0] = True
            if chosen_button == "two" and picked_buttons[1] is False:
                emojis[1] = emoji_id[1]
                picked_buttons[1] = True
            if chosen_button == "three" and picked_buttons[2] is False:
                emojis[2] = emoji_id[2]
                picked_buttons[2] = True

            # Disable the given button
            components.get_component(chosen_button).disable()  # type: ignore
            await gamble_message.edit(
                embed=create_bucket_embed(
                    ctx.author,
                    (
                        "Click the buttons to stop the rolls!",
                        "".join(list(emojis)),
                    ),
                    f"{ctx.author.display_name}'s roll",
                ),
                components=components,
            )

            # Break when they're done picking fish
            if EMOJIS["roll"] not in emojis:
                break

        # Set up the common types
        common_types = [EMOJIS["sand_dollar_stack"],
                        EMOJIS["sand_dollar_pile"]]

        # If they won do nothing special
        if (
            emojis[0] == emojis[1] == emojis[2]
            and EMOJIS["roll"] not in emojis
        ):
            pass

        # If they didn't win 3 in a row see if they won some other way
        elif (
            emojis[0] in common_types
            and emojis[1] in common_types
            or emojis[0] in common_types
            and emojis[2] in common_types
            or emojis[1] in common_types
            and emojis[2] in common_types
        ):
            amount_won = amount / 2
            type_of_balance = "balance"
            emoji = EMOJIS["sand_dollar"]
        elif (
            emojis[0] == EMOJIS["fish_points"]
            and emojis[1] == EMOJIS["fish_points"]
            or emojis[0] == EMOJIS["fish_points"]
            and emojis[2] == EMOJIS["fish_points"]
            or emojis[1] == EMOJIS["fish_points"]
            and emojis[2] == EMOJIS["fish_points"]
        ):
            amount_won = amount / 100
            type_of_balance = "extra_points"
            emoji = EMOJIS["fish_points"]

        # Else show they lost
        else:
            return await ctx.send(f"{ctx.author.mention} lost!")

        # Update their balance with the right type of balance
        async with vbu.Database() as db:
            await db(
                f"""INSERT INTO user_balance (user_id, {type_of_balance}) VALUES ($1, {amount_won})
                ON CONFLICT (user_id) DO UPDATE SET {type_of_balance} = user_balance.{type_of_balance} + {amount_won}""", ctx.author.id)

        # Tell them what they won
        return await ctx.send(
            f"{ctx.author.display_name} has won: {int(amount_won):,} {emoji}"
        )

    @gamble.error
    async def gamble_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R"
        )
        await ctx.send(f"Gamble cooldown, please try again {relative_time}.")


def setup(bot):
    bot.add_cog(Shop(bot))
