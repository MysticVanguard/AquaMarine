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

COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
EPIC_BAG_NAMES = ["Epic Fish Bag", "Epic", "Efb"]
LEGENDARY_BAG_NAMES = ["Legendary Fish Bag", "Legendary", "Lfb"]
MYSTERY_BAG_NAMES = ["Mystery Fish Bag", "Mystery", "Mfb"]


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
        all_names = [
            COMMON_BAG_NAMES, UNCOMMON_BAG_NAMES, RARE_BAG_NAMES, EPIC_BAG_NAMES,
            LEGENDARY_BAG_NAMES, MYSTERY_BAG_NAMES,
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
            "cfb": (COMMON_BAG_NAMES, 50, "Common", inventory_insert_sql.format("cfb")),
            "ufb": (UNCOMMON_BAG_NAMES, 100, "Uncommon", inventory_insert_sql.format("ufb")),
            "rfb": (RARE_BAG_NAMES, 200, "Rare", inventory_insert_sql.format("rfb")),
            "efb": (EPIC_BAG_NAMES, 400, "Epic", inventory_insert_sql.format("efb")),
            "lfb": (LEGENDARY_BAG_NAMES, 500, "Legendary", inventory_insert_sql.format("lfb")),
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
    async def use(self, ctx:commands.Context, item: str):
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

        # See if they are trying to use a bag
        used_bag = None
        if item.title() in COMMON_BAG_NAMES:
            used_bag_humanize, _, used_bag = COMMON_BAG_NAMES
        elif item.title() in UNCOMMON_BAG_NAMES:
            used_bag_humanize, _, used_bag = UNCOMMON_BAG_NAMES
        elif item.title() in RARE_BAG_NAMES:
            used_bag_humanize, _, used_bag = RARE_BAG_NAMES
        elif item.title() in EPIC_BAG_NAMES:
            used_bag_humanize, _, used_bag = EPIC_BAG_NAMES
        elif item.title() in LEGENDARY_BAG_NAMES:
            used_bag_humanize, _, used_bag = LEGENDARY_BAG_NAMES

        # Deal with bag usage
        if used_bag is not None:

            # See if they have the bag they're trying to use
            used_bag = used_bag.lower()
            async with utils.DatabaseConnection() as db:
                user_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id=$1""", ctx.author.id)
                user_bag_count = user_rows[0][used_bag]
            if not user_bag_count:
                return await ctx.send(f"You have no {used_bag_humanize}s!")

            # Remove the bag from their inventory
            async with utils.DatabaseConnection() as db:
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
        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"

        # Tell the user about the fish they rolled
        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity} {new_fish['name']}!"
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)

        # Ask the user if they want to sell the fish
        await self.bot.get_cog("Fishing").ask_to_sell_fish(ctx.author, message, new_fish)

    @commands.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx:commands.Context):
        """
        Shows the users bag inventory.
        """

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
