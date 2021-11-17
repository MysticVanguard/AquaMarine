import random
import asyncio

import discord
from discord.ext import commands
import voxelbotutils as vbu
from datetime import datetime as dt, timedelta

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS
from cogs.utils.misc_utils import create_bucket_embed


FISH_SHOP_EMBED = discord.Embed(title="Fish Shop")
FISH_SHOP_EMBED.add_field(
    name="Fish Bags", value="**These are bags containing a fish**", inline=False)
FISH_SHOP_EMBED.add_field(name="Common Fish Bag <:common_fish_bag:877646166983053383>",
                          value="This gives you one fish from the common rarity \n __100 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Uncommon Fish Bag <:uncommon_fish_bag:877646167146651768>",
                          value="This gives you one fish from the uncommon rarity \n __300 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Rare Fish Bag <:rare_fish_bag:877646167121489930>",
                          value="This gives you one fish from the rare rarity \n __900 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Fish Care", value="These are items to help keep your fish alive", inline=False)
FISH_SHOP_EMBED.add_field(name="Fish Revival <:revival:878297091158474793>",
                          value="This gives you a fish revival to bring your fish back to life \n __2,500 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Fish Flakes <:fish_flakes:877646167188602880>",
                          value="This gives you fish flakes to feed your fish, keeping them alive \n __200 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Tanks", value="These are tanks you can buy to put your fish into, can only be purchased one at a time", inline=False)
FISH_SHOP_EMBED.add_field(
    name="Fish Bowl", value="This gives you a Fish Bowl Tank that you can deposit one small fish into \n __250 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Small Tank", value="This gives you a Small Tank that you can deposit five small fish or one medium fish into\n __2,000 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Medium Tank", value="This gives you a Medium Tank that you can deposit twenty five small fish, five medium fish, or one large fish into \n __12,000 <:sand_dollar:877646167494762586>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Tank Themes", value="These are themes you can buy for your tanks", inline=False)
FISH_SHOP_EMBED.add_field(
    name="Plant Life", value="This gives you the plant life theme for one of your tanks \n __250 <:doubloon:878297091057807400>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Misc", value="These are just some random things", inline=False)
FISH_SHOP_EMBED.add_field(
    name="Fishing Casts", value="This will give you five casts \n __5 <:doubloon:878297091057807400>__", inline=True)
FISH_SHOP_EMBED.add_field(
    name="Sand Dollars", value="This will give you 1,500 sand dollars \n __5 <:doubloon:878297091057807400>__", inline=True)


class Shop(vbu.Cog):

    @commands.command(aliases=["s", "store"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        This command shows everything buyable in the shop, along with their prices.
        """

        await ctx.send(embed=FISH_SHOP_EMBED)

    @commands.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """
        This command buys an item from a shop with the given amount.
        """

        # Say what's valid
        all_names = [
            utils.COMMON_BAG_NAMES, utils.UNCOMMON_BAG_NAMES, utils.RARE_BAG_NAMES, utils.FISH_FLAKES_NAMES, utils.FISH_BOWL_NAMES,
            utils.SMALL_TANK_NAMES, utils.MEDIUM_TANK_NAMES, utils.PLANT_LIFE_NAMES, utils.FISH_REVIVAL_NAMES, utils.CASTS_NAMES, utils.SAND_DOLLAR_NAMES,
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
            "cfb": (utils.COMMON_BAG_NAMES, 100, "Common Fish Bag", inventory_insert_sql.format("cfb")),
            "ufb": (utils.UNCOMMON_BAG_NAMES, 300, "Uncommon Fish Bag", inventory_insert_sql.format("ufb")),
            "rfb": (utils.RARE_BAG_NAMES, 900, "Rare Fish Bag", inventory_insert_sql.format("rfb")),
            "flakes": (utils.FISH_FLAKES_NAMES, 200, "Fish Flakes", inventory_insert_sql.format("flakes")),
            "revival": (utils.FISH_REVIVAL_NAMES, 2500, "Fish Revival", inventory_insert_sql.format("revival")),
            "Fish Bowl": (utils.FISH_BOWL_NAMES, 250, "Fish Bowl", ""),
            "Small Tank": (utils.SMALL_TANK_NAMES, 2000, "Small Tank", ""),
            "Medium Tank": (utils.MEDIUM_TANK_NAMES, 12000, "Medium Tank", ""),
            "Plant Life": (utils.PLANT_LIFE_NAMES, 250, "Plant Life", ""),
            "Casts": (utils.CASTS_NAMES, 5, "Casts", balance_insert_sql.format("casts")),
            "Sand Dollars": (utils.SAND_DOLLAR_NAMES, 1, "Sand Dollars", balance_insert_sql.format("balance"))
        }
        item_name_singular = utils.FISH_BOWL_NAMES + utils.SMALL_TANK_NAMES + \
            utils.MEDIUM_TANK_NAMES + utils.PLANT_LIFE_NAMES
        Doubloon_things = utils.PLANT_LIFE_NAMES + \
            utils.CASTS_NAMES + utils.SAND_DOLLAR_NAMES

        # Work out which of the SQL statements to use
        for table, data in item_name_dict.items():
            possible_entries = data[0]
            if item.title() not in possible_entries:
                continue

            # Unpack the given information
            _, cost, response, db_call = data

            if item.title() in item_name_singular:
                amount = 1
            # See if the user has enough money
            type_of_balance = 'balance'
            emoji = "<:sand_dollar:877646167494762586>"
            if item.title() in Doubloon_things:
                emoji = "<:doubloon:878297091057807400>"
                type_of_balance = 'doubloon'

            full_cost = cost * amount
            if response == "Casts":
                amount = amount * 5
            elif response == "Sand Dollars":
                amount = amount * 1500
            if not await utils.check_price(self.bot, ctx.author.id, full_cost, type_of_balance):
                return await ctx.send(f"You don't have enough {emoji} for this!")

            # here
            check = False
            # Add item to user, check if item is a singular item and if so runs that function
            if item.title() in item_name_singular:
                if await utils.buying_singular(self.bot, ctx.author, ctx, str(response)) is False:
                    return
            else:
                async with vbu.Database() as db:
                    await db(db_call, ctx.author.id, amount)

        # Remove money from the user
        if item.title() in Doubloon_things:
            async with vbu.Database() as db:
                await db("""
                    UPDATE user_balance SET doubloon=doubloon-$1 WHERE user_id = $2""", full_cost, ctx.author.id)
        else:
            async with vbu.Database() as db:
                await db("""
                    UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", full_cost, ctx.author.id)

        # And tell the user we're done
        await ctx.send(f"You bought {amount:,} {response} for {full_cost:,} {emoji}!")

    @commands.command(aliases=["u"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx: commands.Context, item: str):
        """
        This command is only for using fish bags, and is just like using the fish command.
        """

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)

        # See if they are trying to use a bag
        rarity_of_bag = None
        used_bag = None
        used_bag_humanize = None
        if item.title() in utils.COMMON_BAG_NAMES:
            used_bag_humanize, rarity_of_bag, used_bag = utils.COMMON_BAG_NAMES
        elif item.title() in utils.UNCOMMON_BAG_NAMES:
            used_bag_humanize, rarity_of_bag, used_bag = utils.UNCOMMON_BAG_NAMES
        elif item.title() in utils.RARE_BAG_NAMES:
            used_bag_humanize, rarity_of_bag, used_bag = utils.RARE_BAG_NAMES

        # Deal with bag usage
        if used_bag is not None:

            # Make sure these exist
            assert rarity_of_bag
            assert used_bag_humanize

            # See if they have the bag they're trying to use
            rarity_of_bag = rarity_of_bag.lower()
            used_bag = used_bag.lower()
            async with vbu.Database() as db:
                user_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id=$1""", ctx.author.id)
                user_bag_count = user_rows[0][used_bag]
            if not user_bag_count:
                utils.current_fishers.remove(ctx.author.id)
                return await ctx.send(f"You have no {used_bag_humanize}s!")

            # Remove the bag from their inventory
            async with vbu.Database() as db:
                await db(
                    """UPDATE user_item_inventory SET {0}={0}-1 WHERE user_id=$1""".format(
                        used_bag),
                    ctx.author.id,
                )

        # A fish bag wasn't used
        else:
            utils.current_fishers.remove(ctx.author.id)
            return await ctx.send("That is not a usable fish bag!")

        # Get them a new fish
        new_fish = random.choice(
            list(self.bot.fish[rarity_of_bag].values())).copy()

        # Grammar wew
        amount = 0
        owned_unowned = "Unowned"
        a_an = "an" if rarity_of_bag[0].lower() in (
            "a", "e", "i", "o", "u") else "a"
        async with vbu.Database() as db:
            user_inventory = await db("""SELECT * FROM user_fish_inventory WHERE user_id=$1""", ctx.author.id)

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                ctx.author.id
            )
        for row in user_inventory:
            if row['fish'] == new_fish['raw_name']:
                amount = amount + 1
                owned_unowned = "Owned"

        # Tell the user about the fish they rolled
        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity_of_bag} {new_fish['name']}!"
        embed.add_field(
            name=owned_unowned, value=f"You have {amount} {new_fish['name']}", inline=False)
        embed.color = utils.RARITY_CULERS[rarity_of_bag]
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], "new_fish.png")

        # Ask the user if they want to sell the fish
        await utils.ask_to_sell_fish(self.bot, ctx, new_fish, embed=embed, file=fish_file)
        utils.current_fishers.remove(ctx.author.id)

    @commands.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx: commands.Context):
        """
        Shows the user's item inventory.
        """

        fetched_info = []
        async with vbu.Database() as db:
            fetched = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
        if not fetched:
            return await ctx.send("You have no items in your inventory!")

        for row in fetched:
            for key, value in row.items():
                if key == "user_id":
                    continue
                fetched_info.append(value)

        items = ["Common Fish Bag", "Uncommon Fish Bag", "Rare Fish Bag",
                 "Epic Fish Bag", "Legendary Fish Bag", "Fish Flake", "Fish Revives"]
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory")
        for count, name in enumerate(items):
            embed.add_field(name=f'{name}s',
                            value=fetched_info[count], inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def slots(self, ctx: commands.Context):
        """
        This command rolls the slots, costing 5 Sand Dollars.
        """

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")

        # See if the user has enough money
        if not await utils.check_price(self.bot, ctx.author.id, 5, 'balance'):
            return await ctx.send("You don't have enough money for this! (5)")
        utils.current_fishers.append(ctx.author.id)

        # Remove money from the user
        async with vbu.Database() as db:
            await db("""UPDATE user_balance SET balance=balance-5 WHERE user_id = $1""", ctx.author.id)

        # Chooses the random fish for nonwinning rows
        chosen_fish = []
        rarities_of_fish = []
        for i in range(9):
            rarity_random = random.choices(
                *utils.rarity_percentage_finder(1))[0]
            new_fish = random.choice(
                list(utils.utils.EMOJI_RARITIES[rarity_random]))
            rarities_of_fish.append(rarity_random)
            chosen_fish.append(new_fish)

        # Chooses winning fish
        rarity = random.choices(*utils.rarity_percentage_finder(1))[0]
        fish_type = random.choice(list(utils.EMOJI_RARITIES[rarity]))
        emoji_id = utils.EMOJI_RARITIES[rarity][fish_type]

        # Find's the dict of winning fish
        fish_random_name = fish_type.replace("_", " ")
        used_fish = self.bot.fish[rarity][fish_random_name]

        # Checks if the user won
        win_or_lose = random.randint(1, 10)

        # Sends embed of either winning roll or losing roll
        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s roll..."
        row = []
        if win_or_lose == 2:
            for i in range(0, 6, 3):
                row.append(
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i]][chosen_fish[i]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i + 1]][chosen_fish[i + 1]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i + 2]][chosen_fish[i + 2]]}"
                )
            row.append(f"{emoji_id}{emoji_id}{emoji_id}")
            embed.add_field(name="*spent 5 <:sand_dollar:877646167494762586>*",
                            value="\n".join(row), inline=False)
            embed.add_field(
                name="Lucky", value=f"You won {fish_random_name.title()} :)", inline=False)
            async with vbu.Database() as db:

                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                    ctx.author.id
                )
            await utils.ask_to_sell_fish(self.bot, ctx, used_fish, embed=embed)
            utils.current_fishers.remove(ctx.author.id)
        else:
            for i in range(0, 9, 3):
                row.append(
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i]][chosen_fish[i]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i + 1]][chosen_fish[i + 1]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i + 2]][chosen_fish[i + 2]]}"
                )
            embed.add_field(name="*spent 5 <:sand_dollar:877646167494762586>*",
                            value="\n".join(row), inline=False)
            embed.add_field(name="Unlucky", value="You lost :(")
            await ctx.send(embed=embed)
            utils.current_fishers.remove(ctx.author.id)

    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        """
        This command checks the user's balance or another user's balance.
        """

        async with vbu.Database() as db:
            if user:
                other_or_self = f"{user.display_name} has"
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user.id)
            else:
                other_or_self = "You have"
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            if not fetched or not fetched[0]['balance']:
                amount_one = "no"
            else:
                amount_one = f"{fetched[0]['balance']:,}"
            if not fetched or not fetched[0]['doubloon']:
                amount_two = "no"
            else:
                amount_two = f"{fetched[0]['doubloon']:,}"
            if not fetched or not fetched[0]['casts']:
                amount_three = "no"
            else:
                amount_three = f"{fetched[0]['casts']:,}"
        await ctx.send(
            f"""{other_or_self} {amount_one} Sand Dollars <:sand_dollar:877646167494762586>!
            {other_or_self} {amount_two} Doubloons <:doubloon:878297091057807400>!
            {other_or_self} {amount_three} Casts <:Casts:908941461666545674>!
            """
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def sell(self, ctx: commands.Context, fish_sold: str):
        """
        This command sells the specified fish, and it must be out of a tank.
        """

        cost = 0
        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_sold)

        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_sold}!")
        if fish_row[0]['tank_fish']:
            return await ctx.send("That fish is in a tank, please remove it to sell it.")
        if fish_row[0]['fish_alive'] is False:
            async with vbu.Database() as db:
                await db("""DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""", ctx.author.id, fish_sold)
            return await ctx.send(f"You have flushed your dead fish, {fish_sold} for 0 <:sand_dollar:877646167494762586>!")

        multiplier = fish_row[0]['fish_level'] / 20
        for rarity, fish_types in self.bot.fish.items():
            for fish_type, fish_info in fish_types.items():
                if fish_info["raw_name"] == utils.get_normal_name(fish_row[0]['fish']):
                    cost = int(int(fish_info['cost']) / 2)
        sell_money = int(cost * (1 + multiplier))

        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, sell_money,
            )

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + $2""",
                ctx.author.id, sell_money
            )
            await db("""DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""", ctx.author.id, fish_sold)
        await ctx.send(f"You have sold {fish_sold} for {sell_money} <:sand_dollar:877646167494762586>!")

    @commands.command(aliases=["d"])
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def daily(self, ctx: commands.Context):
        """
        This command gives the user a daily reward of 100 Sand Dollars.
        """

        # Adds the money to the users balance
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, 100)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 100""",
                ctx.author.id,
            )
            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, 100)
                ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + 100""",
                ctx.author.id
            )

        # confirmation message
        return await ctx.send("Daily reward of 100 <:sand_dollar:877646167494762586> claimed!")

    @daily.error
    async def daily_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
        await ctx.send(f'Daily reward claimed, please try again {relative_time}.')

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def gamble(self, ctx: commands.Context):
        """
        This command is similar to slots, but doesn't cost anything.
        """

        # Pick the rarity that the user rolled
        i = utils.rarity_percentage_finder(1)
        rarity = random.choices(*i)[0]
        if rarity in ["epic", "rare", "mythic"]:
            rarity = "uncommon"

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)

        async with vbu.Database() as db:
            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_gambled) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_gambled = user_achievements.times_gambled + 1""",
                ctx.author.id
            )

        # Set up some vars for later
        fish_type = []  # The list of fish that they rolled
        emoji_id = []  # The list of fish emojis that they rolled
        emojis = ["<a:roll:886068357378502717>",
                  "<a:roll:886068357378502717>", "<a:roll:886068357378502717>"]
        picked_buttons = [False, False, False]

        # Pick three fish names from their rarity
        for i in range(3):
            fish_type.append(random.choice(
                list(utils.EMOJI_RARITIES_SET_ONE[rarity])))

        # Get the emojis for the fish they rolled
        emoji_id.append([utils.EMOJI_RARITIES_SET_ONE[rarity]
                        [fish_type_single] for fish_type_single in fish_type])
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s roll")
        embed.add_field(
            name="Click the buttons to stop the rolls!", value="".join(emojis))

        # And send the message
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    emoji="1\N{COMBINING ENCLOSING KEYCAP}", custom_id="one"),
                discord.ui.Button(
                    emoji="2\N{COMBINING ENCLOSING KEYCAP}", custom_id="two"),
                discord.ui.Button(
                    emoji="3\N{COMBINING ENCLOSING KEYCAP}", custom_id="three"),
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
                chosen_button_payload = await self.bot.wait_for('component_interaction', timeout=60.0, check=button_check)
                chosen_button = chosen_button_payload.component.custom_id.lower()
            except asyncio.TimeoutError:
                await gamble_message.edit(components=components.disable_components())
                break

            # Update the displayed emoji
            if chosen_button == "one" and picked_buttons[0] is False:
                emojis[0] = emoji_id[0][0]
                picked_buttons[0] = True
            if chosen_button == "two" and picked_buttons[1] is False:
                emojis[1] = emoji_id[0][1]
                picked_buttons[1] = True
            if chosen_button == "three" and picked_buttons[2] is False:
                emojis[2] = emoji_id[0][2]
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
            if "<a:roll:886068357378502717>" not in emojis:
                break

        # Sees if they won the fish they rolled
        if emojis[0] == emojis[1] == emojis[2] and "<a:roll:886068357378502717>" not in emojis:
            fish_won = fish_type[0]
            fish_won_info = None
            for rarity, fish_types in self.bot.fish.items():
                for fish_type, fish_info in fish_types.items():
                    if fish_info["raw_name"] == fish_won:
                        fish_won_info = fish_info
                        break
            assert fish_won_info
            embed = discord.Embed()
            embed.add_field(name=f"{ctx.author.display_name} has won:", value=' '.join(
                fish_won.split('_')).title())
            async with vbu.Database() as db:
                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                    ctx.author.id
                )
            await utils.ask_to_sell_fish(self.bot, ctx, fish_won_info, embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} lost!")

        utils.current_fishers.remove(ctx.author.id)

    @gamble.error
    async def gamble_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
        await ctx.send(f'Gamble cooldown, please try again {relative_time}.')


def setup(bot):
    bot.add_cog(Shop(bot))
