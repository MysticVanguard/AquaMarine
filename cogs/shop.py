import random
import asyncio
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands
import voxelbotutils as vbu

from cogs import utils
from cogs.utils.fish_handler import FishSpecies
from cogs.utils.misc_utils import create_bucket_embed, DAYLIGHT_SAVINGS
from cogs.utils import EMOJIS

# Set up the fields for the shop
SHOP_FIELDS = [
    (
        f"{EMOJIS['amfc']} __AquaMarine Fish Corps State Issued Resources__ {EMOJIS['amfc']}\n"
        f"These are resources bought from the AMFC company.",
        f"**Fish Flakes {EMOJIS['fish_flake']}**\n "
        f"{EMOJIS['bar_empty']}__Price: 30 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Keeps a level **1-20** fish alive for 1 more day\n"
        f"**Fish Pellets {EMOJIS['fish_pellet']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 200 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Keeps a level **21-50** fish alive for 1 more day\n"
        f"**Fish Wafers {EMOJIS['fish_wafer']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 400 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Keeps a level **51+** fish alive for 1 more day\n"
        f"**Fish Revival {EMOJIS['revival']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 2,500 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Can be used to **revive a dead fish**\n"
        f"**Fish Bowl** \n"
        f"{EMOJIS['bar_empty']}__Price: 250 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}The smallest tank, with only **1** Size Point\n",
    ),
    (
        f"{EMOJIS['amfc']} __AquaMarine Fish Corps State Issued Resources__ {EMOJIS['amfc']}\n"
        f"These are resources bought from the AMFC company.",
        f"**Small Tank** \n"
        f"{EMOJIS['bar_empty']}__Price: 5,000 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Enough to hold a medium fish, has **5** Size Points\n"
        f"**Medium Tank** \n"
        f"{EMOJIS['bar_empty']}__Price: 50,000 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}The biggest tank, with **25** Size Points, able to hold a large fish\n"
        f"**New Location Unlock** \n"
        f"{EMOJIS['bar_empty']}__Price: 25 {EMOJIS['doubloon']}__\n"
        f"{EMOJIS['bar_empty']}Unlocks one of the advanced locations\n",
    ),
    (
        f"{EMOJIS['gfu']} __Golden Fishers Union Item Market__ {EMOJIS['gfu']}\n"
        f"These are items sold by the GFU",
        f"**Five Fishing Casts {EMOJIS['casts']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 1 {EMOJIS['doubloon']}__\n"
        f"{EMOJIS['bar_empty']}Gives you **5** casts to use for fishing\n"
        f"**Inverted Fish Bag {EMOJIS['inverted_fish_bag']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 10 {EMOJIS['doubloon']}__\n"
        f"{EMOJIS['bar_empty']}Gives a bag that can be a fish of any rarity, but is **inverted**\n"
        f"**High Level Fish Bag {EMOJIS['high_level_fish_bag']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 40,000 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}Gives a bag that can be a fish of any rarity, but is **level 25-50**\n"
        f"**Experience Potion {EMOJIS['experience_potion']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 75,000 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}When used on a fish, gives them **25,000 Experience**\n",
    ),
    (
        f"{EMOJIS['gfu']} __Golden Fishers Union Item Market__ {EMOJIS['gfu']}\n"
        f"These are items sold by the GFU",
        f"**Mutation Potion {EMOJIS['mutation_potion']}** \n"
        f"{EMOJIS['bar_empty']}__ Price: 50 {EMOJIS['doubloon']}__\n"
        f"{EMOJIS['bar_empty']}When used on a fish, makes that fish **inverted**\n"
        f"**Plant Life** \n"
        f"{EMOJIS['bar_empty']}__Price: 250 {EMOJIS['doubloon']}__\n"
        f"{EMOJIS['bar_empty']}A nice green **plant themed background** for your aquarium, can be veiwed with {EMOJIS['bar_empty']}`preview` \n"
        f"**Fish Points {EMOJIS['fish_points']}** \n"
        f"{EMOJIS['bar_empty']}__Price: 500 {EMOJIS['sand_dollar']}__\n"
        f"{EMOJIS['bar_empty']}One permanant point for the **\"Fish Points\" leaderboard**\n",
    ),
]


class Shop(vbu.Cog):
    @commands.command(
        aliases=["s", "store"],
        application_command_meta=commands.ApplicationCommandMeta(),
    )
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

    @commands.command(
        aliases=["b"],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="item",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The item you want to buy",
                    choices=[
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Flakes", value="ff"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Pellets", value="fp"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Wafers", value="fw"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Revivals", value="fr"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Bowl", value="fb"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Small Tank", value="st"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Medium Tank", value="mt"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="New Location Unlock", value="nlu"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Five Fishing Casts", value="fc"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Inverted Fish Bag", value="ifb"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="High Level Fish Bag", value="hlfb"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Experience Potion", value="e"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Mutation Potion", value="m"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Plant Life", value="pl"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Points", value="p"
                        ),
                    ],
                ),
                discord.ApplicationCommandOption(
                    name="amount",
                    type=discord.ApplicationCommandOptionType.integer,
                    description="The number of the provided item you want to buy",
                    required=False,
                ),
            ]
        ),
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """
        This command buys an item from a shop with the given amount.
        """

        await utils.check_registered(self.bot, ctx, ctx.author.id)

        if amount <= 0:
            return await ctx.send("Please enter a positive amount")

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
            "ifb": (
                utils.INVERTED_BAG_NAMES,
                10,
                "Inverted Fish Bag",
                inventory_insert_sql.format("ifb"),
            ),
            "hlfb": (
                utils.HIGH_LEVEL_BAG_NAMES,
                40000,
                "High Level Fish Bag",
                inventory_insert_sql.format("hlfb"),
            ),
            "flakes": (
                utils.FISH_FLAKES_NAMES,
                30,
                "Fish Flakes",
                inventory_insert_sql.format("flakes"),
            ),
            "pellets": (
                utils.FISH_PELLETS_NAMES,
                200,
                "Fish Pellets",
                inventory_insert_sql.format("pellets"),
            ),
            "wafers": (
                utils.FISH_WAFERS_NAMES,
                400,
                "Fish Wafers",
                inventory_insert_sql.format("wafers"),
            ),
            "revival": (
                utils.FISH_REVIVAL_NAMES,
                2500,
                "Fish Revival",
                inventory_insert_sql.format("revival"),
            ),
            "Fish Bowl": (utils.FISH_BOWL_NAMES, 250, "Fish Bowl", ""),
            "Small Tank": (utils.SMALL_TANK_NAMES, 5000, "Small Tank", ""),
            "Medium Tank": (utils.MEDIUM_TANK_NAMES, 50000, "Medium Tank", ""),
            "Plant Life": (utils.PLANT_LIFE_NAMES, 250, "Plant Life", ""),
            "Fish Points": (
                utils.FISH_POINTS_NAMES,
                500,
                "Fish Points",
                balance_insert_sql.format("extra_points"),
            ),
            "Casts": (
                utils.CASTS_NAMES,
                1,
                "Casts",
                balance_insert_sql.format("casts"),
            ),
            "Experience Potion": (
                utils.EXPERIENCE_POTION_NAMES,
                75000,
                "Experience Potions",
                inventory_insert_sql.format("experience_potions"),
            ),
            "Mutation Potion": (
                utils.MUTATION_POTION_NAMES,
                50,
                "Mutation Potions",
                inventory_insert_sql.format("mutation_potions"),
            ),
            "New Location Unlock": (
                utils.NEW_LOCATION_UNLOCK_NAMES,
                25,
                "New Location Unlocks",
                inventory_insert_sql.format("new_location_unlock"),
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
            + utils.MUTATION_POTION_NAMES
            + utils.INVERTED_BAG_NAMES
            + utils.NEW_LOCATION_UNLOCK_NAMES
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

            # Check if they have enough money
            if not await utils.check_price(
                self.bot, ctx.author.id, full_cost, type_of_balance
            ):
                return await ctx.send(f"You don't have enough {emoji} for this!")

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
            break

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
        await ctx.send(f"You bought {amount:,} {response} for {full_cost:,} {emoji}!")

    @commands.command(
        aliases=["u"],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="item",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The item you want to use",
                ),
            ]
        ),
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx: commands.Context, *, item: str):
        """
        This command is for using fish bags and potions.
        """

        await utils.check_registered(self.bot, ctx, ctx.author.id)

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
                inventory_rows = await utils.user_item_inventory_db_call(ctx.author.id)

                # If they don't have any potions tell them that
                if inventory_rows[0][type_of_potion] == 0:
                    return await ctx.send("You have no potions of that type!")

            # Find the fish with that name
            async with vbu.Database() as db:
                fish_rows = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish != '' AND death_time != Null""",
                    ctx.author.id,
                )

            fish_rows_names = []
            for row in fish_rows:
                fish_rows_names.append(row["fish_name"])

            # Add the buttons to the message
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(emoji=EMOJIS["aqua_smile"]),
                ),
            )
            # Asks for the name of the tank the user is putting the theme on and makes sure it is correct
            message = await ctx.send(
                f"Press the button to specify fish you want to give the potion to",
                components=components,
            )

            def button_check(payload):
                if payload.message.id != message.id:
                    return False
                return payload.user.id == ctx.author.id

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Timed out asking for interaction, no available slots given."
                )

            name, interaction = await utils.create_modal(
                self.bot,
                chosen_button_payload,
                "Choose a fish",
                "Fish in a tank to give potion to",
            )

            if not name:
                return await ctx.send(
                    "Timed out asking for name, no available name given."
                )

            # Find the fish with that name
            await interaction.response.defer_update()
            async with vbu.Database() as db:
                fish_row = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                    ctx.author.id,
                    name,
                )

            # Check for if the fish exists
            if not fish_row:
                return await ctx.send("There is no fish in a tank with that name.")

            # Remove one potion from the user
            async with vbu.Database() as db:
                await db(
                    f"""UPDATE user_item_inventory SET {type_of_potion} = {type_of_potion} - 1 Where user_id = $1""",
                    ctx.author.id,
                )

            # If they use an experience potion...
            if item.title() in utils.EXPERIENCE_POTION_NAMES:

                # Add 10k xp to the fish
                await utils.xp_finder_adder(ctx.author.id, name, 25000, False)
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

                    await db(
                        """UPDATE user_fish_inventory SET fish_skin = $1 where user_id = $2 AND fish = $3""",
                        "inverted",
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
                death_date = fish_row[0]["death_time"] + \
                    timedelta(days=30, hours=0)

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

        # Deal with bag usage
        if used_bag is not None:

            # If its a bag with rarity just lower it, else pick a random rarity
            if rarity_of_bag:
                rarity_of_bag = rarity_of_bag.lower()
            else:
                rarity_of_bag = random.choices(
                    *utils.rarity_percentage_finder(0))[0]

            # Lower the used bag
            used_bag = used_bag.lower()

            # Find the users items
            async with vbu.Database() as db:
                user_rows = await utils.user_item_inventory_db_call(ctx.author.id)

                # Find how many bags of that type they have
                user_bag_count = user_rows[0][used_bag]

            # If they have none tell them they have no bags and remove them from current fishers
            if not user_bag_count:
                return await ctx.send(f"You have no {used_bag_humanize}s!")

            # See which fish they caught by taking a random fish from the chosen rarity
            chosen_fish = random.choice(
                utils.FishSpecies.get_rarity(rarity_of_bag))

            while chosen_fish.name in utils.past_fish:
                chosen_fish = random.choice(
                    utils.FishSpecies.get_rarity(rarity_of_bag))

            # find if its skinned
            fish_skin = ""
            if type_of_bag == "Inverted":
                fish_skin = random.choice(chosen_fish.skins)

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
            return await ctx.send("That is not a usable item!")

        # Grammar
        a_an = "an" if rarity_of_bag[0].lower() in (
            "a", "e", "i", "o", "u") else "a"

        # Get their fish inventory, add 1 to their times caught in achievements, subtract 1 from their casts
        async with vbu.Database() as db:
            user_inventory = await utils.user_fish_inventory_db_call(ctx.author.id)

            # Achievements
            await db(
                """UPDATE user_achievements SET times_caught = times_caught + 1 WHERE user_id = $1""",
                ctx.author.id,
            )
            await db(
                """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                ctx.author.id,
            )

        # Find out how many of those fish they caught previously
        amount = 0
        for row in user_inventory:
            if row["fish"] == chosen_fish.name:
                amount += 1

        # Set the fish file to the fishes image

        # Tell the user about the fish they caught
        owned_unowned = "Owned" if amount > 0 else "Unowned"
        embed = discord.Embed(
            title=f"{EMOJIS['aqua_fish']} {ctx.author.display_name} caught {a_an} *{rarity_of_bag}* {chosen_fish.size} **{chosen_fish.name.replace('_', ' ').title()}**!"
        )
        embed.add_field(
            name=owned_unowned,
            value=f"You have {amount} **{chosen_fish.name.replace('_', ' ').title()}**",
            inline=False,
        )
        embed.set_image(url="attachment://new_fish.png")
        embed.color = utils.RARITY_CULERS[rarity_of_bag]

        # Ask if they want to sell the fish they just caught or keep it
        message, _ = await utils.ask_to_sell_fish(
            self.bot,
            ctx,
            None,
            level_inserted=level,
            chosen_fish=chosen_fish,
            skin=fish_skin,
            embed=embed,
        )
        await ctx.send(message)

    @commands.command(
        aliases=["inv"], application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx: commands.Context):
        """
        Shows the user's item inventory.
        """

        # Get the users item inventory
        await utils.check_registered(self.bot, ctx, ctx.author.id)
        async with vbu.Database() as db:
            fetched = await utils.user_item_inventory_db_call(ctx.author.id)

        # list of tuples with the name and the name in the database
        items = [
            ("High Level Fish Bag", "hlfb"),
            ("Inverted Fish Bag", "ifb"),
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
            ("Fishing Boots", "fishing_boots"),
            ("Trash Toys", "trash_toys"),
            ("Super Food", "super_food"),
            ("New Location Unlock", "new_location_unlock"),
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
                name = (name[0].replace(" Fish", ""), name[1])

            # If they have more than one of the item add an s
            if fetched[0][name[1]] > 1 and name[0][-1] != "s":
                name = (name[0] + "s", name[1])

            # add the emoji, name, and amount formatted to the title list
            title_value.append(
                f"{utils.EMOJIS[emoji]} {name[0]} : {fetched[0][name[1]]}"
            )

            # If the lists length is 2 add the two strings in it as name and value and reset the list
            if len(title_value) == 2:
                embed.add_field(
                    name=title_value[0], value=title_value[1], inline=True)
                title_value = []
            elif items[len(items) - 1][0] == name[0]:
                embed.add_field(
                    name=title_value[0], value="** **", inline=True)
                title_value = []

        # Send the embed
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["bal"],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    type=discord.ApplicationCommandOptionType.user,
                    description="The user's balance you want to check (leave blank for your own)",
                    required=False,
                ),
            ]
        ),
    )
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx: commands.Context, user: discord.User = None):
        """
        This command checks the user's balance or another user's balance.
        """

        await utils.check_registered(self.bot, ctx, ctx.author.id)
        if user:
            await utils.check_registered(self.bot, ctx, user.id)
        async with vbu.Database() as db:

            # If they specified someone get that users balance
            if user:
                other_or_self = f"{user.display_name}'s"
                fetched = await utils.user_balance_db_call(user.id)

            # Else get your own balance
            else:
                other_or_self = "Your"
                fetched = await utils.user_balance_db_call(ctx.author.id)

            # If theres none of each type of balance say no, otherwise say that balance
            if not fetched[0]["balance"]:
                amount_one = "no"
            else:
                amount_one = f"{fetched[0]['balance']:,}"
            if not fetched[0]["doubloon"]:
                amount_two = "no"
            else:
                amount_two = f"{fetched[0]['doubloon']:,}"
            if not fetched[0]["casts"]:
                amount_three = "no"
            else:
                amount_three = f"{fetched[0]['casts']:,}"

        # Send the users balance
        embed = discord.Embed(title=f"{other_or_self} Balance")
        embed.add_field(
            name="Sand Dollars:", value=f"{amount_one} {EMOJIS['sand_dollar']}"
        )
        embed.add_field(name="Doubloons:",
                        value=f"{amount_two} {EMOJIS['doubloon']}")
        embed.add_field(
            name="Casts:", value=f"{amount_three} {EMOJIS['casts']}")
        await ctx.send(embed=embed)

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="fish_sold",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The fish you want to sell",
                ),
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True)
    async def sell(self, ctx: commands.Context, *, fish_sold: str):
        """
        This command sells the specified fish or tank
        """

        # Set the cost to 0
        cost = 0

        # Get the fish row for the fish specified
        await utils.check_registered(self.bot, ctx, ctx.author.id)
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
        fish = FishSpecies.get_fish(fish_row[0]["fish"])
        cost = fish.cost

        # Get the sell money using the level multiplier
        sell_money = int(cost * (1 + multiplier))

        # Add the money to their balance
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
                ctx.author.id,
                sell_money,
            )

            # Achievements
            await db(
                """UPDATE user_achievements SET money_gained = money_gained + $2 WHERE user_id = $1""",
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

    @commands.command(
        aliases=["d"], application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def daily(self, ctx: commands.Context):
        """
        This command gives the user a daily reward of up to 2,500 Sand Dollars.
        """

        # Check if they voted and if not tell them they need to vote
        await utils.check_registered(self.bot, ctx, ctx.author.id)
        if await utils.get_user_voted(self.bot, ctx.author.id) is False:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "Please vote and then run this command to get the daily reward!"
            )

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="Stop Spinning", custom_id="stop")
            ),
        )
        embed = discord.Embed(title="Click the button to stop the wheel!")
        file = discord.File(
            "C:/Users/JT/Pictures/Aqua/assets/images/background/daily_wheel.gif",
            "win_wheel.gif",
        )
        embed.set_image(url="attachment://win_wheel.gif")
        embed.add_field(
            name=f"Spinning...",
            value="Green = 400\nBlue = 800\nPurple = 1,600\nYellow = 2,400\nPink = 4,800",
        )
        daily_message = await ctx.send(embed=embed, components=components, file=file)

        # Make the button check

        def button_check(payload):
            if payload.message.id != daily_message.id:
                return False
            return payload.user.id == ctx.author.id

        # Wait for them to click a button
        try:
            await self.bot.wait_for(
                "component_interaction", check=button_check, timeout=60
            )
        except TimeoutError:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("Timed out waiting for click, try again.")

        reward = random.choices(
            [400, 800, 1600, 2400, 4800], [0.5, 0.25, 0.125, 0.083, 0.042]
        )[0]

        # Adds the money to the users balance
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
                ctx.author.id,
                reward,
            )
            # Achievements
            await db(
                """UPDATE user_achievements SET money_gained = money_gained + $2 WHERE user_id = $1""",
                ctx.author.id,
                reward,
            )

        # confirmation message
        embed = discord.Embed(title="Click the button to stop the wheel!")
        file = discord.File(
            f"C:/Users/JT/Pictures/Aqua/assets/images/background/{str(reward)}_wheel_win.png",
            "win_wheel.png",
        )
        embed.set_image(url="attachment://win_wheel.png")
        embed.add_field(
            name=f"Daily reward of {reward:,} {EMOJIS['sand_dollar']} claimed!",
            value="Green = 400\nBlue = 800\nPurple = 1,600\nYellow = 2,400\nPink = 4,800",
        )
        await daily_message.delete()
        return await ctx.send(embed=embed, file=file)

    @daily.error
    async def daily_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R"
        )
        await ctx.send(f"Daily reward claimed, please try again {relative_time}.")

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="amount",
                    type=discord.ApplicationCommandOptionType.integer,
                    description="The amount you want to gamble (multiple of 100)",
                    required=False,
                )
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def gamble(self, ctx: commands.Context, amount: int = 100):
        """
        This command gambles sand dollars for more sand dollars
        """

        # See if the user has enough money and enters a correct amount
        await utils.check_registered(self.bot, ctx, ctx.author.id)

        if amount % 100 != 0:
            return await ctx.send("Please enter an amount divisible by 100")

        if amount <= 0:
            return await ctx.send("Please enter a positive amount of sand dollars")

        async with vbu.Database() as db:
            bottle_caps = await utils.user_item_inventory_db_call(ctx.author.id)

        # Make the button check
        def yes_no_check(payload):
            if payload.message.id != yes_no_message.id:
                return False
            self.bot.loop.create_task(payload.response.defer_update())
            return payload.user.id == ctx.author.id

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="Yes", custom_id="yes"),
                discord.ui.Button(label="No", custom_id="no"),
            ),
        )
        needed_caps = amount / 100
        bottle_caps = bottle_caps[0]["pile_of_bottle_caps"]
        if bottle_caps >= needed_caps:
            yes_no_message = await ctx.send(
                f"Would you like to spend {int(needed_caps)} bottle caps instead of sand dollars? (You have {bottle_caps} bottle caps)",
                components=components,
            )

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=yes_no_check
                )
                chosen_button = chosen_button_payload.component.custom_id.lower()
            except asyncio.TimeoutError:
                await yes_no_message.edit(components=components.disable_components())
                chosen_button = "no"
        else:
            chosen_button = "no"

        async with vbu.Database() as db:
            if chosen_button == "yes":
                await db(
                    """UPDATE user_item_inventory SET pile_of_bottle_caps=pile_of_bottle_caps-$2 WHERE user_id = $1""",
                    ctx.author.id,
                    needed_caps,
                )
            else:
                if not await utils.check_price(
                    self.bot, ctx.author.id, amount, "balance"
                ):
                    return await ctx.send(
                        f"You don't have enough sand dollars for this! ({amount})"
                    )
                # Remove money from the user
                await db(
                    """UPDATE user_balance SET balance=balance-$2 WHERE user_id = $1""",
                    ctx.author.id,
                    amount,
                )

            async with vbu.Database() as db:
                # Achievements
                await db(
                    """UPDATE user_achievements SET times_gambled = times_gambled + 1 WHERE user_id = $1""",
                    ctx.author.id,
                )

        # Set up some vars for later
        item_values = []  # The list of values that they rolled
        emoji_id = []  # The list of emojis that they rolled
        emojis = [EMOJIS["roll"]] * 3
        picked_buttons = [False] * 3

        # Pick three fish names from their rarity
        for i in range(3):
            item_values.append(random.randint(1, 31))

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
                chosen_button = chosen_button_payload.component.custom_id.lower()
            except asyncio.TimeoutError:
                await gamble_message.edit(components=components.disable_components())
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
                    1,
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
        if emojis[0] == emojis[1] == emojis[2] and EMOJIS["roll"] not in emojis:
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
                f"""UPDATE user_balance SET {type_of_balance} = {type_of_balance} + {amount_won} WHERE user_id = $1""",
                ctx.author.id,
            )

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
