# Badly made code for a shop, still WIP as it doesnt work lol
import random
import asyncio
import typing

import discord
from discord.ext import commands

import utils


FISH_SHOP_EMBED = discord.Embed(title="Fish Shop")
FISH_SHOP_EMBED.add_field(name="Fish Bags", value="These are bags containing a fish of a random rarity", inline=False)
FISH_SHOP_EMBED.add_field(name="Common Fish Bag", value="This gives you one fish with normal chances COST 50", inline=True)
FISH_SHOP_EMBED.add_field(name="Uncommon Fish Bag", value="This gives you one fish with increased chances COST 100", inline=True)
FISH_SHOP_EMBED.add_field(name="Rare Fish Bag", value="This gives you one fish with higher chances COST 200", inline=True)
FISH_SHOP_EMBED.add_field(name="Epic Fish Bag", value="This gives you one fish with substantially better chances COST 400", inline=True)
FISH_SHOP_EMBED.add_field(name="Legendary Fish Bag", value="This gives you one fish with extremely better chances COST 500", inline=True)
FISH_SHOP_EMBED.add_field(name="Mystery Fish Bag", value="This gives you one bag of a random rarity COST 250", inline=True)


class Shop(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(aliases=["s"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        Shows embed full of shop information.
        """

        await ctx.send(embed=FISH_SHOP_EMBED)

    @commands.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: typing.Optional[str], amount: typing.Optional[int] = 1):
        """
        Buys a certain amount of an item in the shop.
        """

        # Say what's valid
        common_names = ["Common Fish Bag", "Common", "Cfb"]
        uncommon_names = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
        rare_names = ["Rare Fish Bag", "Rare", "Rfb"]
        epic_names = ["Epic Fish Bag", "Epic", "Efb"]
        legendary_names = ["Legendary Fish Bag", "Legendary", "Lfb"]
        mystery_names = ["Mystery Fish Bag", "Mystery", "Mfb"]
        all_names = [common_names, uncommon_names, rare_names, epic_names, legendary_names, mystery_names]

        # See if they gave a valid item
        if not any([item.title() in name_list for name_list in all_names]):
            return await ctx.send("That is not an available item")

        # Set up SQL statements for each of the tiered inserts
        inventory_insert_sql = (
            "INSERT INTO user_item_inventory (user_id, {0}) VALUES ($1, $2) ON CONFLICT "
            "(user_id) DO UPDATE SET {0}=user_item_inventory.{0}+excluded.{0}"
        )
        item_name_dict = {
            "cfb": (common_names, 50, "Common", inventory_insert_sql.format("cfb")),
            "ufb": (uncommon_names, 100, "Uncommon", inventory_insert_sql.format("ufb")),
            "rfb": (rare_names, 200, "Rare", inventory_insert_sql.format("rfb")),
            "efb": (epic_names, 400, "Epic", inventory_insert_sql.format("efb")),
            "lfb": (legendary_names, 500, "Legendary", inventory_insert_sql.format("lfb")),
        }

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
                _, rarity_response, db_call = item_name_dict[rarity_type]
                cost = 250
            else:
                cost, rarity_response, db_call = data

            # See if the user has enough money
            if not await self.check_price(ctx.author.id, cost):
                return await ctx.send("You don't have enough money for this!")

            # Add fish bag to user
            async with utils.DatabaseConnection() as db:
                await db(db_call, ctx.author.id, amount)

        # Remove money from the user
        async with utils.DatabaseConnection() as db:
            await db("""
                UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", cost, ctx.author.id)

        # And tell the user we're done
        await ctx.send(f"You Bought {amount:,} {rarity_response} Fish Bag for {amount * cost:,}!")

    async def check_price(self, user_id: int, cost: int) -> bool:
        """
        Returns if a user_id has enough money based on the cost.
        """

        async with utils.DatabaseConnection() as db:
            user_rows = await db(
                """SELECT balance FROM user_balance WHERE user_id=$1""",
                user_id,
            )
            user_balance = user_rows[0]['balance']
        return user_balance >= cost

    @commands.command(aliases=["u"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx:commands.Context, used_item: str):
        """
        Uses an item from your inventory.
        """

        rarity_chances = {
            "cfb": {"common": .6689, "uncommon": .2230, "rare": .0743, "epic": .0248, "legendary": .0082, "mythic": .0008},
            "ufb": {"common": .6062, "uncommon": .2423, "rare": .0967, "epic": .0385, "legendary": .0154, "mythic": .0009},
            "rfb": {"common": .5156, "uncommon": .2578, "rare": .1289, "epic": .0645, "legendary": .0322, "mythic": .0010},
            "efb": {"common": .4558, "uncommon": .2605, "rare": .1490, "epic": .0850, "legendary": .0486, "mythic": .0011},
            "lfb": {"common": .3843, "uncommon": .2558, "rare": .1701, "epic": .1134, "legendary": .0752, "mythic": .0012},
        }

        item = used_item
        fetched = ""

        if item.title() == "Common Fish Bag" or item.title() == "Common" or item.title() == "Cfb":
            chances = rarity_chances["cfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT cfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['cfb']
            if not fetched:
                return await ctx.send("You have no Common Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET cfb=cfb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Uncommon Fish Bag" or item.title() == "Uncommon" or item.title() == "Ufb":
            chances = rarity_chances["ufb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT ufb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['ufb']
            if not fetched:
                return await ctx.send("You have no Uncommon Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET ufb=ufb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Rare Fish Bag" or item.title() == "Rare" or item.title() == "Rfb":
            chances = rarity_chances["rfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT rfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['rfb']
            if not fetched:
                return await ctx.send("You have no Rare Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET rfb=rfb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Epic Fish Bag" or item.title() == "Epic" or item.title() == "Efb":
            chances = rarity_chances["efb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT efb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['efb']
            if not fetched:
                return await ctx.send("You have no Epic Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET efb=efb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Legendary Fish Bag" or item.title() == "Legendary" or item.title() == "Lfb":
            chances = rarity_chances["lfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT lfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['lfb']
            if not fetched:
                return await ctx.send("You have no Legendary Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET lfb=lfb-1 WHERE user_id = $1""", ctx.author.id)

        print(chances)
        rarity = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [chances["common"], chances["uncommon"], chances["rare"], chances["epic"], chances["legendary"], chances["mythic"],]
        )[0]
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.94, .05, .01]
        )[0]
        new_fish = random.choice(list(self.bot.fish[rarity].values()))

        if special == "normal":
            pass
        elif special == "inverted":
            new_fish = utils.make_inverted(new_fish)
        elif special == "golden":
            new_fish = utils.make_golden(new_fish)

        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"

        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity} {new_fish['name']}!"
        embed.set_image(url="attachment://new_fish.png")

        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)

        emojis = [844594478392147968, 844594468580491264]
        gen = (x for x in self.bot.emojis if x.id in emojis)
        for i in gen:
            await message.add_reaction(i)

        check = lambda reaction, user: reaction.emoji.id in emojis and user.id == ctx.author.id and reaction.message.id == message.id
        try:
            choice = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            choice = "sell" if choice[0].emoji.id == 844594478392147968 else "keep"
        except asyncio.TimeoutError:
            await ctx.send("Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
            choice = "sell"

        if choice == "sell":
            async with utils.DatabaseConnection() as db:
                await db("""
                    INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2;
                    """, ctx.author.id, new_fish["cost"])
            await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
            return utils.make_pure(new_fish, special)

        await ctx.send("What do you want to name your new fish? (32 character limit)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32

        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"You're new fish **{name}** has been added to your bucket!")

        except asyncio.TimeoutError:
            name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
            return await ctx.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")

        finally:
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1, $2, $3)""", ctx.author.id, new_fish["raw_name"], name)
            return utils.make_pure(new_fish, special)

    @commands.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx:commands.Context):
        '''Shows the users bag inventory'''

        fetched_info = []
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
        if not fetched:
            return await ctx.send("You have no items in your inventory!")
        for info in fetched:
            for values in info:
                if values < 1000000:
                    fetched_info.append(values)
        bags = ["Common Fish Bag", "Uncommon Fish Bag", "Rare Fish Bag", "Epic Fish Bag", "Legendary Fish Bag"]
        count = 0
        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s Inventory"
        for name in bags:
            embed.add_field(name=f'{name}\'s',value=fetched_info[count], inline=False)
            count += 1
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Shop(bot))
