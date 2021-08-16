import random
from time import time
import typing
import asyncio

import discord
from discord.ext import commands
import voxelbotutils as vbu
from datetime import datetime as dt, timedelta

from cogs import utils
from cogs.utils.misc_utils import create_bucket_embed


FISH_SHOP_EMBED = discord.Embed(title="Fish Shop")
FISH_SHOP_EMBED.add_field(name="Fish Bags", value="These are bags containing a fish of a random rarity", inline=False)
FISH_SHOP_EMBED.add_field(name="Common Fish Bag <:common_fish_bag:851974760510521375>", value="This gives you one fish with normal chances \n __50 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Uncommon Fish Bag <:uncommon_fish_bag:851974792864595988>", value="This gives you one fish with increased chances \n __100 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Rare Fish Bag <:rare_fish_bag:851974785088618516>", value="This gives you one fish with higher chances \n __200 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Epic Fish Bag <:epic_fish_bag:851974770467930118>", value="This gives you one fish with substantially better chances \n __400 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Legendary Fish Bag <:legendary_fish_bag:851974777567838258>", value="This gives you one fish with extremely better chances \n __500 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Mystery Fish Bag <:mystery_fish_bag:851975891659391006>", value="This gives you one bag of a random rarity \n __250 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Fish Care", value="These are items to help keep your fish alive", inline=False)
FISH_SHOP_EMBED.add_field(name="Fish Revival <:fish_flakes:852053373111894017>", value="This gives you a fish revival to bring your fish back to life \n __1,000 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Fish Flakes <:fish_flakes:852053373111894017>", value="This gives you fish flakes to feed your fish, keeping them alive \n __10 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Tanks", value="These are tanks you can buy to put your fish into, can only be purchased one at a time", inline=False)
FISH_SHOP_EMBED.add_field(name="Fish Bowl", value="This gives you a Fish Bowl Tank that you can deposit one small fish into \n __100 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Small Tank", value="This gives you a Small Tank that you can deposit five small fish or one medium fish into\n __500 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Medium Tank", value="This gives you a Medium Tank that you can deposit twenty five small fish, five medium fish, or one large fish into \n __2,500 <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Tank Themes", value="These are themes you can buy for your tanks", inline=False)
FISH_SHOP_EMBED.add_field(name="Plant Life", value="This gives you the plant life theme for one of your tanks \n __1,000 <:sand_dollar:852057443503964201>__", inline=True)


class Shop(vbu.Cog):

    @vbu.command(aliases=["s"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        This command shows everything buyable in the shop, along with their prices.
        """

        await ctx.send(embed=FISH_SHOP_EMBED)

    @vbu.command(aliases=["b"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """
        This command buys an item from a shop with the given value.
        """

        # Say what's valid
        all_names = [
            utils.COMMON_BAG_NAMES, utils.UNCOMMON_BAG_NAMES, utils.RARE_BAG_NAMES, utils.EPIC_BAG_NAMES,
            utils.LEGENDARY_BAG_NAMES, utils.MYSTERY_BAG_NAMES, utils.FISH_FLAKES_NAMES, utils.FISH_BOWL_NAMES,
            utils.SMALL_TANK_NAMES, utils.MEDIUM_TANK_NAMES, utils.PLANT_LIFE_NAMES, utils.FISH_REVIVAL_NAMES,
        ]

        # See if they gave a valid item
        if not any([item.title() in name_list for name_list in all_names]):
            return await ctx.send("That is not an available item")

        # Set up SQL statements for each of the tiered inserts
        inventory_insert_sql = (
            "INSERT INTO user_item_inventory (user_id, {0}) VALUES ($1, $2) ON CONFLICT "
            "(user_id) DO UPDATE SET {0}=user_item_inventory.{0}+excluded.{0}"
        )
        item_name_dict = {
            "cfb": (utils.COMMON_BAG_NAMES, 50, "Common Fish Bag", inventory_insert_sql.format("cfb")),
            "ufb": (utils.UNCOMMON_BAG_NAMES, 100, "Uncommon Fish Bag", inventory_insert_sql.format("ufb")),
            "rfb": (utils.RARE_BAG_NAMES, 200, "Rare Fish Bag", inventory_insert_sql.format("rfb")),
            "efb": (utils.EPIC_BAG_NAMES, 400, "Epic Fish Bag", inventory_insert_sql.format("efb")),
            "lfb": (utils.LEGENDARY_BAG_NAMES, 500, "Legendary Fish Bag", inventory_insert_sql.format("lfb")),
            "mfb": (utils.MYSTERY_BAG_NAMES, 250),
            "flakes": (utils.FISH_FLAKES_NAMES, 10, "Fish Flakes", inventory_insert_sql.format("flakes")),
            "revival": (utils.FISH_REVIVAL_NAMES, 1000, "Fish Revival", inventory_insert_sql.format("revival")),
            "Fish Bowl": (utils.FISH_BOWL_NAMES, 100, "Fish Bowl", ""),
            "Small Tank": (utils.SMALL_TANK_NAMES, 500, "Small Tank", ""),
            "Medium Tank": (utils.MEDIUM_TANK_NAMES, 2500, "Medium Tank", ""),
            "Plant Life": (utils.PLANT_LIFE_NAMES, 1000, "Plant Life", "")
        }
        item_name_singular = [
            utils.FISH_BOWL_NAMES, utils.SMALL_TANK_NAMES, utils.MEDIUM_TANK_NAMES, utils.PLANT_LIFE_NAMES
        ]

        # Work out which of the SQL statements to use
        for table, data in item_name_dict.items():
            possible_entries = data[0]
            if item.title() not in possible_entries:
                continue

            # Unpack the given information
            if possible_entries[-1] == "Mfb":
                rarity_type = random.choices(
                    ["cfb", "ufb", "rfb", "efb", "lfb"],
                    [.5, .3, .125, .05, .025,]
                )[0]
                _, _, response, db_call = item_name_dict[rarity_type]
                cost = 250
            else:
                _, cost, response, db_call = data
            for names in item_name_singular:
                if item.title() in names:
                    amount = 1
            # See if the user has enough money

            full_cost = cost * amount
            if not await utils.check_price(self.bot, ctx.author.id, full_cost):
                return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:852057443503964201> for this!")

            # here
            check = False
            # Add item to user, check if item is a singular item and if so runs that function
            for item_names in item_name_singular:
                if item.title() in item_names:
                    check = True
            print(check)
            if check is True:
                print("yes")
                if await utils.buying_singular(self.bot, ctx, str(response)) is False:
                    return
            else:
                print("no")
                async with self.bot.database() as db:
                    await db(db_call, ctx.author.id, amount)

        # Remove money from the user
        async with self.bot.database() as db:
            await db("""
                UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", full_cost, ctx.author.id)

        # And tell the user we're done
        await ctx.send(f"You bought {amount:,} {response} for {full_cost:,} <:sand_dollar:852057443503964201>!")

    @vbu.command(aliases=["u"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx: commands.Context, item: str):
        """
        This command is only for using fish bags, it is just like using the fish command.
        """

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)

        rarity_chances = {
            "cfb": {"common": .6689, "uncommon": .2230, "rare": .0743, "epic": .0248, "legendary": .0082, "mythic": .0008},
            "ufb": {"common": .6062, "uncommon": .2423, "rare": .0967, "epic": .0385, "legendary": .0154, "mythic": .0009},
            "rfb": {"common": .5156, "uncommon": .2578, "rare": .1289, "epic": .0645, "legendary": .0322, "mythic": .0010},
            "efb": {"common": .4558, "uncommon": .2605, "rare": .1490, "epic": .0850, "legendary": .0486, "mythic": .0011},
            "lfb": {"common": .3843, "uncommon": .2558, "rare": .1701, "epic": .1134, "legendary": .0752, "mythic": .0012},
        }

        # See if they are trying to use a bag
        used_bag = None
        if item.title() in utils.COMMON_BAG_NAMES:
            used_bag_humanize, _, used_bag = utils.COMMON_BAG_NAMES
        elif item.title() in utils.COMMON_BAG_NAMES:
            used_bag_humanize, _, used_bag = utils.COMMON_BAG_NAMES
        elif item.title() in utils.RARE_BAG_NAMES:
            used_bag_humanize, _, used_bag = utils.RARE_BAG_NAMES
        elif item.title() in utils.EPIC_BAG_NAMES:
            used_bag_humanize, _, used_bag = utils.EPIC_BAG_NAMES
        elif item.title() in utils.LEGENDARY_BAG_NAMES:
            used_bag_humanize, _, used_bag = utils.LEGENDARY_BAG_NAMES

        # Deal with bag usage
        if used_bag is not None:

            # See if they have the bag they're trying to use
            used_bag = used_bag.lower()
            async with self.bot.database() as db:
                user_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id=$1""", ctx.author.id)
                user_bag_count = user_rows[0][used_bag]
            if not user_bag_count:
                return await ctx.send(f"You have no {used_bag_humanize}s!")

            # Remove the bag from their inventory
            async with self.bot.database() as db:
                await db(
                    """UPDATE user_item_inventory SET {0}={0}-1 WHERE user_id=$1""".format(used_bag),
                    ctx.author.id,
                )

        # A fish bag wasn't used
        else:
            return

        # Get what rarity of fish they rolled
        rarity_names = ["common", "uncommon", "rare", "epic", "legendary", "mythic"]
        chances = rarity_chances[used_bag]
        rarity = random.choices(
            rarity_names,
            [chances[n] for n in rarity_names]
        )[0]

        # See if they rolled a modified fish
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.94, .05, .01]
        )[0]

        # Get them a new fish
        new_fish = random.choice(list(self.bot.fish[rarity].values())).copy()

        # Modify the fish if necessary
        if special == "inverted":
            new_fish = utils.make_inverted(new_fish)
        elif special == "golden":
            new_fish = utils.make_golden(new_fish)

        # Grammar wew
        amount = 0
        owned_unowned = "Unowned"
        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
        async with self.bot.database() as db:
            user_inventory = await db("""SELECT * FROM user_fish_inventory WHERE user_id=$1""", ctx.author.id)
        for row in user_inventory:
            if row['fish'] == new_fish['raw_name']:
                amount = amount + 1
                owned_unowned = "Owned"

        # Tell the user about the fish they rolled
        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity} {new_fish['name']}!"
        embed.add_field(name=owned_unowned, value=f"You have {amount} {new_fish['name']}", inline=False)
        embed.color = utils.RARITY_CULERS[rarity]
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)

        # Ask the user if they want to sell the fish
        await utils.ask_to_sell_fish(self.bot, ctx.author, message, new_fish)

        utils.current_fishers.remove(ctx.author.id)


    @vbu.command(aliases=["inv"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx: commands.Context):
        """
        Shows your bag inventory.
        """

        fetched_info = []
        async with self.bot.database() as db:
            fetched = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
        if not fetched:
            return await ctx.send("You have no items in your inventory!")
        for info in fetched:
            for values in info:
                if values < 1000000:
                    fetched_info.append(values)
        items = ["Common Fish Bag", "Uncommon Fish Bag", "Rare Fish Bag", "Epic Fish Bag", "Legendary Fish Bag", "Fish Flake"]
        count = 0
        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s Inventory"
        for name in items:
            embed.add_field(name=f'{name}s', value=fetched_info[count], inline=True)
            count += 1
        await ctx.send(embed=embed)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def slots(self, ctx: commands.Context):
        """
        This command roles the slots.
        """

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)

        # See if the user has enough money
        if not await utils.check_price(self.bot, ctx.author.id, 5):
            return await ctx.send("You don't have enough money for this! (5)")

        # Remove money from the user
        async with self.bot.database() as db:
            await db("""UPDATE user_balance SET balance=balance-5 WHERE user_id = $1""", ctx.author.id)

        # Chooses the random fish for nonwinning rows
        chosen_fish = []
        rarities_of_fish = []
        for i in range(9):
            rarity_random = random.choices(*utils.rarity_percentage_finder(1))[0]
            new_fish = random.choice(list(utils.utils.EMOJI_RARITIES[rarity_random]))
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
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i+2]][chosen_fish[i+2]]}"
                )
            row.append(f"{emoji_id}{emoji_id}{emoji_id}")
            embed.add_field(name="*spent 5 <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Lucky", value=f"You won {fish_random_name.title()} :)", inline=False)
            message = await ctx.send(embed=embed)
            await utils.ask_to_sell_fish(ctx.author, message, used_fish)
        else:
            for i in range(0, 9, 3):
                row.append(
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i]][chosen_fish[i]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                    f"{utils.EMOJI_RARITIES[rarities_of_fish[i+2]][chosen_fish[i+2]]}"
                )
            embed.add_field(name="*spent 5 <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Unlucky", value="You lost :(")
            await ctx.send(embed=embed)
            utils.current_fishers.remove(ctx.author.id)

    @vbu.command(aliases=["bal"])
    @vbu.bot_has_permissions(send_messages=True)
    async def balance(self, ctx: commands.Context, user: discord.Member = None):
        """
        This command checks your balance or another users.
        """

        async with self.bot.database() as db:
            if user:
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user.id)
                if fetched:
                    return await ctx.send(f"{user.display_name} has {fetched[0]['balance']:,} <:sand_dollar:852057443503964201>!")
                return await ctx.send(f"{user.display_name} has no Sand Dollars <:sand_dollar:852057443503964201>!")
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            if fetched:
                return await ctx.send(f"You have {fetched[0]['balance']:,} <:sand_dollar:852057443503964201>!")
            return await ctx.send("You have no Sand Dollars <:sand_dollar:852057443503964201>!")

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def sell(self, ctx: commands.Context, fish_sold: str):
        """
        This command sells the specified fish, and it must be out of a tank.
        """

        cost = 0
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_sold)

        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_sold}!")
        if fish_row[0]['tank_fish']:
            return await ctx.send("That fish is in a tank, please remove it to sell it.")
        multiplier = fish_row[0]['fish_level'] / 10
        for rarity, fish_types in self.bot.fish.items():
            for fish_type, fish_info in fish_types.items():
                if fish_info["raw_name"] == utils.get_normal_name(fish_row[0]['fish']):
                    cost = int(fish_info['cost'])
        sell_money = int(cost * (1 + multiplier))
        async with self.bot.database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, sell_money,
            )
            await db("""DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""", ctx.author.id, fish_sold)
        await ctx.send(f"You have sold {fish_sold} for {sell_money} <:sand_dollar:852057443503964201>!")

    @vbu.command(aliases=["d"])
    @vbu.cooldown.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @vbu.bot_has_permissions(send_messages=True)
    async def daily(self, ctx: commands.Context):
        """
        This command gives you a daily reward of 100 Sand Dollars.
        """

        # Adds the money to the users balance
        async with self.bot.database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, 100)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 100""",
                ctx.author.id,
            )

        # confirmation message
        return await ctx.send("Daily reward of 100 Sand Dollars <:sand_dollar:852057443503964201> claimed!")

    @daily.error
    async def daily_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = error.retry_after
        if 5_400 > time >= 3_600:
            form = 'hour'
            time /= 60 * 60
        elif time > 3_600:
            form = 'hours'
            time /= 60 * 60
        elif 90 > time >= 60:
            form = 'minute'
            time /= 60
        elif time >= 60:
            form = 'minutes'
            time /= 60
        elif time < 1.5:
            form = 'second'
        else:
            form = 'seconds'
        await ctx.send(f'Daily reward claimed, please try again in {round(time)} {form}.')

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def gamble(self, ctx: commands.Context):
        """
        The gamble command.
        """

        # Pick the rarity that the user rolled
        i = utils.rarity_percentage_finder(1)
        rarity = random.choices(*i)[0]
        if rarity in ["epic", "rare", "mythic"]:
            rarity = "uncommon"

        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)

        # Set up some vars for later
        fish_type = []  # The list of fish that they rolled
        emoji_id = []  # The list of fish emojis that they rolled
        emojis = ["<a:first_set_roll:875259843571748924>", "<a:first_set_roll:875259843571748924>", "<a:first_set_roll:875259843571748924>"]
        picked_buttons = [False, False, False]

        # Pick three fish names from their rarity
        for i in range(3):
            fish_type.append(random.choice(list(utils.EMOJI_RARITIES_SET_ONE[rarity])))

        # Get the emojis for the fish they rolled
        emoji_id.append([utils.EMOJI_RARITIES_SET_ONE[rarity][fish_type_single] for fish_type_single in fish_type])
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s roll")
        embed.add_field(name="Click the buttons to stop the rolls!", value="".join(emojis))

        # And send the message
        components = vbu.MessageComponents(
            vbu.ActionRow(
                vbu.Button(custom_id="one", emoji="1\N{COMBINING ENCLOSING KEYCAP}"),
                vbu.Button(custom_id="two", emoji="2\N{COMBINING ENCLOSING KEYCAP}"),
                vbu.Button(custom_id="three", emoji="3\N{COMBINING ENCLOSING KEYCAP}"),
            ),
        )
        gamble_message = await ctx.send(embed=embed, components=components)

        # Make the button check
        def button_check(payload):
            if payload.message.id != gamble_message.id:
                return False
            self.bot.loop.create_task(payload.defer_update())
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
            components.get_component(chosen_button).disable()
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
            if "<a:first_set_roll:875259843571748924>" not in emojis:
                break

        # Sees if they won the fish they rolled
        if emojis[0] == emojis[1] == emojis[2]:
            fish_won = fish_type[0]
            for rarity, fish_types in self.bot.fish.items():
                for fish_type, fish_info in fish_types.items():
                    if fish_info["raw_name"] == fish_won:
                        fish_won_info = fish_info
                        break
            message = await ctx.send(f"{ctx.author.mention} has won a {' '.join(fish_won.split('_')).title()}!")
            await utils.ask_to_sell_fish(self.bot, ctx.author, message, fish_won_info)
        else:
            await ctx.send(f"{ctx.author.mention} lost!")

        utils.current_fishers.remove(ctx.author.id)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def revive(self, ctx: commands.Context, fish: str):

        # Get database vars
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish)
            revival_count = await db("""SELECT revival FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # Checks that error
        if not fish_row:
            return await ctx.send(
                f"You have no fish named {fish}!",
                allowed_mentions=discord.AllowedMentions.none()
                )
        if fish_row[0]["fish_alive"] is True:
            return await ctx.send("That fish is alive!")
        if revival_count == 0:
            return await ctx.send("You have no revivals!")

        # If the fish isn't in a tank, it has no death timer, but if it is it's set to three days
        if fish_row[0]["tank_fish"] != '':
            death_timer = None
            message = f"{fish} is now alive!"
        else:
            death_timer = (dt.utcnow() + timedelta(days=3))
            message = f"{fish} is now alive, and will die {vbu.TimeFormatter(death_timer)}!"

        # Set the database values
        async with self.bot.database() as db:
            await db("""UPDATE user_fish_inventory SET fish_alive = True, death_time = $3 WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish, death_timer)
            await db("""UPDATE user_fish_inventory SET revival = revival - 1 WHERE user_id = $1""", ctx.author.id)

        # Send message
        await ctx.send(
            message,
            allowed_mentions=discord.AllowedMentions.none()
            )





def setup(bot):
    bot.add_cog(Shop(bot))
