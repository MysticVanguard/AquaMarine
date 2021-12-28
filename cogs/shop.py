import random
import asyncio
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands
import voxelbotutils as vbu

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS
from cogs.utils.misc_utils import create_bucket_embed
from cogs.utils import EMOJIS


SHOP_FIELDS = [
    (
        "Fish Shop\n*These are neutral items for sale.*",
        f"**Fish Points {EMOJIS['fish_points']}**\n"
        f"One permanant point for the leaderboard \n"
        f" __500 {EMOJIS['sand_dollar']}__\n"
        f"**Fishing Casts {EMOJIS['casts']}**\n"
        f"Five casts \n"
        f" __5 {EMOJIS['doubloon']}__\n"
        f"**Sand Dollars {EMOJIS['sand_dollar']}**\n"
        f"1,500 sand dollars \n"
        f" __1 {EMOJIS['doubloon']}__\n"
        f"**Fish Revival {EMOJIS['revival']}**\n"
        f"Fish revival to bring your fish back to life \n"
        f" __2,500 {EMOJIS['sand_dollar']}__\n"
        f"**Plant Life**\nThe plant life theme for one of your tanks \n"
        f" __250 {EMOJIS['doubloon']}__",
    ),
    (
        f"{EMOJIS['amfc']} __AquaMarine Fish Corps State Issued Resources__ {EMOJIS['amfc']}\n"
        f"These are resources bought from the AMFC company.",
        f"**Fish Flakes {EMOJIS['fish_flakes']}**\n"
        f"Fish flakes to feed a fish that is level 1-20, keeping them alive \n"
        f" __200 {EMOJIS['sand_dollar']}__\n"
        f"**Fish Pellets {EMOJIS['fish_pellets']}**\n"
        f"Fish pellets to feed a fish that is level 21-50, keeping them alive \n"
        f" __500 {EMOJIS['sand_dollar']}__\n"
        f"**Fish Wafers {EMOJIS['fish_wafers']}**\n"
        f"Fish wafers to feed a fish that is level 51+, keeping them alive \n"
        f" __1000 {EMOJIS['sand_dollar']}__\n"
        f"**Fish Bowl**\n"
        f"Fish Bowl Tank that you can deposit one small fish into \n"
        f" __500 {EMOJIS['sand_dollar']}__\n"
        f"**Small Tank**\n"
        f"Small Tank that you can deposit five small fish or one medium fish into\n"
        f" __2,000 {EMOJIS['sand_dollar']}__\n"
        f"**Medium Tank**\n"
        f"Medium Tank that you can deposit twenty five small fish, five medium fish, or one large fish into \n"
        f" __12,000 {EMOJIS['sand_dollar']}__",
    ),
    (
        f"{EMOJIS['gfu']} __Golden Fishers Union Item Market__ {EMOJIS['gfu']}\n"
        f"These are items sold by the GFU",
        f"**Common Fish Bag {EMOJIS['common_fish_bag']}**\n"
        f"One fish from the common rarity \n"
        f" __50 {EMOJIS['sand_dollar']}__\n"
        f"**Uncommon Fish Bag {EMOJIS['uncommon_fish_bag']}**\n"
        f"One fish from the uncommon rarity \n"
        f" __150 {EMOJIS['sand_dollar']}__\n"
        f"**Rare Fish Bag {EMOJIS['rare_fish_bag']}**\n"
        f"One fish from the rare rarity \n"
        f" __750 {EMOJIS['sand_dollar']}__\n"
        f"**Inverted Fish Bag {EMOJIS['inverted_fish_bag']}**\n"
        f"One inverted fish from any rarity \n"
        f" __100,000 {EMOJIS['sand_dollar']}__\n"
        f"**High Level Fish Bag {EMOJIS['high_level_fish_bag']}**\n"
        f"One fish from any rarity between the levels 10-50 \n"
        f" __75,000 {EMOJIS['sand_dollar']}__\n"
        f"**Feeding Potion {EMOJIS['feeding_potion']}**\n"
        f"Feeding potion that will make your fish full for 30 days \n"
        f" __10,000 {EMOJIS['sand_dollar']}__\n"
        f"**Experience Potion {EMOJIS['experience_potion']}**\n"
        f"Experience potion that gives your fish 10,000 experience \n"
        f" __40,000 {EMOJIS['sand_dollar']}__\n"
        f"**Mutation Potion {EMOJIS['mutation_potion']}**\n"
        f"Mutation potion that turns one of your fish inverted \n"
        f" __50 {EMOJIS['doubloon']}__",
    ),
]


class Shop(vbu.Cog):
    @commands.command(aliases=["s", "store"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        This command shows everything buyable in the shop, along with their prices.
        """

        fields = []
        for field in SHOP_FIELDS:
            [fields.append(i) for i in utils.get_fixed_field(field)]
        await utils.paginate(ctx, fields, ctx.author)

    @commands.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """
        This command buys an item from a shop with the given amount.
        """

        # Say what's valid
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
        item_name_singular = (
            utils.FISH_BOWL_NAMES
            + utils.SMALL_TANK_NAMES
            + utils.MEDIUM_TANK_NAMES
            + utils.PLANT_LIFE_NAMES
        )
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

            # See if the user has enough money
            type_of_balance = "balance"
            emoji = EMOJIS["sand_dollar"]
            if item.title() in Doubloon_things:
                emoji = EMOJIS["doubloon"]
                type_of_balance = "doubloon"

            full_cost = cost * amount
            if response == "Casts":
                amount = amount * 5
            elif response == "Sand Dollars":
                amount = amount * 1500
            if not await utils.check_price(
                self.bot, ctx.author.id, full_cost, type_of_balance
            ):
                return await ctx.send(
                    f"You don't have enough {emoji} for this!"
                )

            # here
            check = False
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

        # Remove money from the user
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

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(
                f"{ctx.author.display_name}, you're already fishing!"
            )

        # See if they are trying to use a bag
        rarity_of_bag = None
        used_bag = None
        used_bag_humanize = None
        type_of_bag = None
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
        elif item.title() in (
            utils.EXPERIENCE_POTION_NAMES
            + utils.MUTATION_POTION_NAMES
            + utils.FEEDING_POTION_NAMES
        ):
            if item.title() in utils.EXPERIENCE_POTION_NAMES:
                type_of_potion = "experience_potions"
            elif item.title() in utils.MUTATION_POTION_NAMES:
                type_of_potion = "mutation_potions"
            elif item.title() in utils.FEEDING_POTION_NAMES:
                type_of_potion = "feeding_potions"

            async with vbu.Database() as db:
                inventory_rows = await db(
                    """SELECT * FROM user_item_inventory WHERE user_id = $1""",
                    ctx.author.id,
                )

                if (
                    not inventory_rows
                    or inventory_rows[0][type_of_potion] == 0
                ):
                    return await ctx.send("You have no potions of that type!")

                await db(
                    f"""UPDATE user_item_inventory SET {type_of_potion} = {type_of_potion} - 1 Where user_id = $1""",
                    ctx.author.id,
                )

            message = await ctx.send(
                "Enter the name of the fish you want to give that potion to."
            )

            def check(m):
                return m.author == ctx.author and m.channel == message.channel

            try:
                name_message = await self.bot.wait_for(
                    "message", timeout=60.0, check=check
                )
                name = name_message.content
            except asyncio.TimeoutError:
                return await message.channel.send(
                    "Timed out asking for fish name"
                )

            async with vbu.Database() as db:
                fish_row = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                    ctx.author.id,
                    name,
                )

            if not fish_row:
                return await ctx.send("There is no fish with that name.")

            if item.title() in utils.EXPERIENCE_POTION_NAMES:
                await utils.xp_finder_adder(ctx.author, name, 10000, False)
                async with vbu.Database() as db:
                    new_fish_rows = await db(
                        """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                        ctx.author.id,
                        name,
                    )
                return await ctx.send(
                    f"{new_fish_rows[0]['fish_name']} is now level {new_fish_rows[0]['fish_level']}, {new_fish_rows[0]['fish_xp']}/{new_fish_rows[0]['fish_xp_max']}"
                )
            if item.title() in utils.MUTATION_POTION_NAMES:
                async with vbu.Database() as db:
                    mutated = "inverted_" + fish_row[0]["fish"]
                    await db(
                        """UPDATE user_fish_inventory SET fish = $1 where user_id = $2 AND fish = $3""",
                        mutated,
                        ctx.author.id,
                        fish_row[0]["fish"],
                    )

                    return await ctx.send(
                        f"{fish_row[0]['fish_name']}looks kind of strange now..."
                    )
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

                return await ctx.send("That fish feels strangely full now...")

        utils.current_fishers.append(ctx.author.id)
        # Deal with bag usage
        if used_bag is not None:

            # See if they have the bag they're trying to use
            if rarity_of_bag:
                rarity_of_bag = rarity_of_bag.lower()
            else:
                rarity_of_bag = random.choices(
                    *utils.rarity_percentage_finder(0)
                )[0]

            used_bag = used_bag.lower()
            async with vbu.Database() as db:
                user_rows = await db(
                    """SELECT * FROM user_item_inventory WHERE user_id=$1""",
                    ctx.author.id,
                )
                user_bag_count = user_rows[0][used_bag]
            if not user_bag_count:
                utils.current_fishers.remove(ctx.author.id)
                return await ctx.send(f"You have no {used_bag_humanize}s!")

                # Get them a new fish
            new_fish = random.choice(
                list(self.bot.fish[rarity_of_bag].values())
            ).copy()
            while new_fish["raw_name"] in utils.past_fish:
                new_fish = random.choice(
                    list(self.bot.fish[rarity_of_bag].values())
                ).copy()
            if type_of_bag == "Inverted":
                new_fish = utils.make_inverted(new_fish.copy())
            level = 0
            if type_of_bag == "High Level":
                level = random.randint(10, 50)
            # Remove the bag from their inventory
            async with vbu.Database() as db:
                await db(
                    f"""UPDATE user_item_inventory SET {used_bag}={used_bag}-1 WHERE user_id=$1""",
                    ctx.author.id,
                )

        # A fish bag wasn't used
        elif used_bag is None:
            utils.current_fishers.remove(ctx.author.id)
            return await ctx.send("That is not a usable fish bag!")

        # Grammar wew
        amount = 0
        owned_unowned = "Unowned"
        a_an = (
            "an"
            if rarity_of_bag[0].lower() in ("a", "e", "i", "o", "u")
            else "a"
        )
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

        utils.current_fishers.remove(ctx.author.id)

    @commands.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx: commands.Context):
        """
        Shows the user's item inventory.
        """

        fetched_info = []
        async with vbu.Database() as db:
            fetched = await db(
                """SELECT * FROM user_item_inventory WHERE user_id = $1""",
                ctx.author.id,
            )
        if not fetched:
            return await ctx.send("You have no items in your inventory!")

        for row in fetched:
            for key, value in row.items():
                if key == "user_id":
                    continue
                fetched_info.append(value)

        items = [
            "Common Fish Bag",
            "Uncommon Fish Bag",
            "Rare Fish Bag",
            "Epic Fish Bag",
            "Legendary Fish Bag",
            "Fish Flake",
            "Fish Revives",
        ]
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory")
        for count, name in enumerate(items):
            embed.add_field(
                name=f"{name}s", value=fetched_info[count], inline=True
            )
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
            if user:
                other_or_self = f"{user.display_name} has"
                fetched = await db(
                    """SELECT * FROM user_balance WHERE user_id = $1""",
                    user.id,
                )
            else:
                other_or_self = "You have"
                fetched = await db(
                    """SELECT * FROM user_balance WHERE user_id = $1""",
                    ctx.author.id,
                )
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
        await ctx.send(
            f"""{other_or_self} {amount_one} Sand Dollars {EMOJIS["sand_dollar"]}!
            {other_or_self} {amount_two} Doubloons {EMOJIS["doubloon"]}!
            {other_or_self} {amount_three} Casts {EMOJIS["casts"]}!
            """
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def sell(self, ctx: commands.Context, *, fish_sold: str):
        """
        This command sells the specified fish, and it must be out of a tank.
        """

        cost = 0
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id,
                fish_sold,
            )

        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_sold}!")
        if fish_row[0]["tank_fish"]:
            return await ctx.send(
                "That fish is in a tank, please remove it to sell it."
            )
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

        multiplier = fish_row[0]["fish_level"] / 20
        for rarity, fish_types in self.bot.fish.items():
            for fish_type, fish_info in fish_types.items():
                if fish_info["raw_name"] == utils.get_normal_name(
                    fish_row[0]["fish"]
                ):
                    cost = int(fish_info["cost"])
        sell_money = int(cost * (1 + multiplier))

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
            await db(
                """DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""",
                ctx.author.id,
                fish_sold,
            )
        await ctx.send(
            f"You have sold {fish_sold} for {sell_money} {EMOJIS['sand_dollar']}!"
        )

    @commands.command(aliases=["d"])
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def daily(self, ctx: commands.Context):
        """
        This command gives the user a daily reward of 500 Sand Dollars.
        """

        # # Adds the money to the users balance
        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_balance (user_id, balance) VALUES ($1, 500)
        #         ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 500""",
        #         ctx.author.id,
        #     )
        #     # Achievements
        #     await db(
        #         """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, 500)
        #         ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + 500""",
        #         ctx.author.id,
        #     )

        # # confirmation message
        # return await ctx.send(
        #     f"Daily reward of 500 {EMOJIS['sand_dollar']} claimed!"
        # )

        if await utils.get_user_voted(self.bot, ctx.author.id) is False:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "Please vote and then run this command to get the special daily reward for the event!"
            )

        # print(await utils.get_user_voted(self.bot, ctx.author.id))
        # if ctx.author.id in utils.current_fishers:
        #     return await ctx.send(
        #         f"{ctx.author.display_name}, you're already fishing!"
        #     )

        # # Grammar
        # new_fish = self.bot.fish["epic"]["gingerbread axolotl"]
        # a_an = "an"
        # rarity = "epic"
        # # Tell the user about the fish they caught
        # embed = discord.Embed(
        #     title=f"{EMOJIS['aqua_fish']} {ctx.author.display_name} caught {a_an} *{rarity}* {new_fish['size']} **{new_fish['name']}**!"
        # )
        # embed.set_image(url="attachment://new_fish.png")
        # embed.color = utils.RARITY_CULERS[rarity]

        # # Set the fish file to the fishes image
        # print("test")
        # fish_file = discord.File(new_fish["image"], "new_fish.png")
        # await ctx.send(
        #     "On the first day of fishmas, fish santa gave to me\n\tA Gingerbread Axolotl",
        #     file=fish_file,
        # )
        # # Ask if they want to sell the fish they just caught or keep it
        # await utils.ask_to_sell_fish(self.bot, ctx, new_fish, embed=embed)

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, revival) VALUES ($1, 2)
        #         ON CONFLICT (user_id) DO UPDATE SET revival = user_item_inventory.revival + 2""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the second day of fishmas, fish santa gave to me\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, flakes) VALUES ($1, 3)
        #         ON CONFLICT (user_id) DO UPDATE SET flakes = user_item_inventory.flakes + 3""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the third day of fishmas, fish santa gave to me\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_balance (user_id, casts) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET casts = user_balance.casts + 4""",
                ctx.author.id
            )
        return await ctx.send("On the fourth day of fishmas, fish santa gave to me\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, wafers) VALUES ($1, 5)
        #         ON CONFLICT (user_id) DO UPDATE SET wafers = user_item_inventory.wafers + 5""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the fifth day of fishmas, fish santa gave to me\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, rfb) VALUES ($1, 6)
        #         ON CONFLICT (user_id) DO UPDATE SET rfb = user_item_inventory.rfb + 6""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the sixth day of fishmas, fish santa gave to me\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # # Adds the money to the users balance
        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_balance (user_id, balance) VALUES ($1, 7000)
        #         ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 7000""",
        #         ctx.author.id,
        #     )
        #     # Achievements
        #     await db(
        #         """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, 7000)
        #         ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + 7000""",
        #         ctx.author.id
        #     )

        # # confirmation message
        # return await ctx.send("On the seventh day of fishmas, fish santa gave to me:\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #             await db(
        #                 """INSERT INTO user_item_inventory (user_id, pellets) VALUES ($1, 8)
        #                 ON CONFLICT (user_id) DO UPDATE SET pellets = user_item_inventory.pellets + 8""",
        #                 ctx.author.id
        #             )
        # return await ctx.send("On the eighth day of fishmas, fish santa gave to me\n\tEight fish food pellets\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #             await db(
        #                 """INSERT INTO user_balance (user_id, extra_points) VALUES ($1, 9)
        #                 ON CONFLICT (user_id) DO UPDATE SET extra_points = user_balance.extra_points + 9""",
        #                 ctx.author.id
        #             )
        # return await ctx.send("On the ninth day of fishmas, fish santa gave to me\n\tNine leaderboard points\n\tEight fish food pellets\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, ufb) VALUES ($1, 10)
        #                 ON CONFLICT (user_id) DO UPDATE SET ufb = user_item_inventory.ufb + 10""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the tenth day of fishmas, fish santa gave to me\n\tTen uncommon bags\n\tNine leaderboard points\n\tEight fish food pellets\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_item_inventory (user_id, cfb) VALUES ($1, 11)
        #                 ON CONFLICT (user_id) DO UPDATE SET cfb = user_item_inventory.cfb + 11""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the eleventh day of fishmas, fish santa gave to me\n\tEleven common fish bags\n\tTen uncommon bags\n\tNine leaderboard points\n\tEight fish food pellets\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

        # async with vbu.Database() as db:
        #     await db(
        #         """INSERT INTO user_balance (user_id, doubloon) VALUES ($1, 12)
        #                 ON CONFLICT (user_id) DO UPDATE SET doubloon = user_balance.doubloon + 12""",
        #         ctx.author.id
        #     )
        # return await ctx.send("On the twelfth day of fishmas, fish santa gave to me\n\tTwelve shining doubloons\n\tEleven common fish bags\n\tTen uncommon bags\n\tNine leaderboard points\n\tEight fish food pellets\n\tSeven thousand dollars\n\tSix rare bags of fish\n\tFive fish wafers\n\tFour fishing casts\n\tThree fish flakes\n\tTwo revivals\n\tAnd a Gingerbread Axolotl")

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
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def gamble(self, ctx: commands.Context):
        """
        This command costs 50 sand dollars and will give a fish bag
        """
        items = {
            "cfb": (
                EMOJIS["common_fish_bag"],
                "Common Fish Bag",
            ),
            "ufb": (
                EMOJIS["uncommon_fish_bag"],
                "Uncommon Fish Bag",
            ),
            "rfb": (EMOJIS["rare_fish_bag"], "Rare Fish Bag"),
        }

        # See if the user has enough money
        if not await utils.check_price(self.bot, ctx.author.id, 50, "balance"):
            return await ctx.send(
                "You don't have enough sand dollars for this! (50)"
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
                """UPDATE user_balance SET balance=balance-50 WHERE user_id = $1""",
                ctx.author.id,
            )

        # Set up some vars for later
        item_type = []  # The list of fish that they rolled
        emoji_id = []  # The list of fish emojis that they rolled
        emojis = [EMOJIS["roll"]] * 3
        picked_buttons = [False] * 3

        # Pick three fish names from their rarity
        for i in range(3):
            item_type.append(
                random.choices(["cfb", "ufb", "rfb"], [0.5, 0.3, 0.2])
            )

        # Get the emojis for the fish they rolled
        for item in item_type:
            emoji_id.append(items[item[0]][0])
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s roll")
        embed.add_field(
            name="Click the buttons to stop the rolls!", value="".join(emojis)
        )

        # And send the message
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

        # Sees if they won the fish they rolled
        if (
            emojis[0] == emojis[1] == emojis[2]
            and EMOJIS["roll"] not in emojis
        ):
            bag_won = item_type[0][0]
            async with vbu.Database() as db:
                await db(
                    """INSERT INTO user_item_inventory (user_id, {0}) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET {0} = user_item_inventory.{0} + 1""".format(
                        bag_won
                    ),
                    ctx.author.id,
                )
            return await ctx.send(
                f"{ctx.author.display_name} has won: {items[item_type[0][0]][1]}"
            )
        await ctx.send(f"{ctx.author.mention} lost!")

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
