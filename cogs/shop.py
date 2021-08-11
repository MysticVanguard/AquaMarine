import random
import typing
import voxelbotutils as vbu
import asyncio

import discord
from discord.ext import commands

import utils


FISH_SHOP_EMBED = discord.Embed(title="Fish Shop")
FISH_SHOP_EMBED.add_field(name="Fish Bags", value="These are bags containing a fish of a random rarity", inline=False)
FISH_SHOP_EMBED.add_field(name="Common Fish Bag <:common_fish_bag:851974760510521375>", value="This gives you one fish with normal chances \n __50 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Uncommon Fish Bag <:uncommon_fish_bag:851974792864595988>", value="This gives you one fish with increased chances \n __100 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Rare Fish Bag <:rare_fish_bag:851974785088618516>", value="This gives you one fish with higher chances \n __200 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Epic Fish Bag <:epic_fish_bag:851974770467930118>", value="This gives you one fish with substantially better chances \n __400 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Legendary Fish Bag <:legendary_fish_bag:851974777567838258>", value="This gives you one fish with extremely better chances \n __500 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Mystery Fish Bag <:mystery_fish_bag:851975891659391006>", value="This gives you one bag of a random rarity \n __250 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Fish Food", value="This is food that can be fed to fish to level them up", inline=False)
FISH_SHOP_EMBED.add_field(name="Fish Flakes <:fish_flakes:852053373111894017>", value="This gives you fish flakes to feed your fish, keeping them alive \n __5 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Tanks", value="These are tanks you can buy to put your fish into, can only be purchased one at a time", inline=False)
FISH_SHOP_EMBED.add_field(name="Fish Bowl", value="This gives you a Fish Bowl Tank that you can deposit one small fish into \n __100 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Small Tank", value="This gives you a Small Tank that you can deposit five small fish or one medium fish into\n __500 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Medium Tank", value="This gives you a Medium Tank that you can deposit twenty five small fish, five medium fish, or one large fish into \n __2500 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)
FISH_SHOP_EMBED.add_field(name="Tank Themes", value="These are themes you can buy for your tanks", inline=False)
FISH_SHOP_EMBED.add_field(name="Plant Life", value="This gives you the plant life theme for one of your tanks \n __1000 Sand Dollars <:sand_dollar:852057443503964201>__", inline=True)


COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
EPIC_BAG_NAMES = ["Epic Fish Bag", "Epic", "Efb"]
LEGENDARY_BAG_NAMES = ["Legendary Fish Bag", "Legendary", "Lfb"]
MYSTERY_BAG_NAMES = ["Mystery Fish Bag", "Mystery", "Mfb"]
FISH_FLAKES_NAMES = ["Fish Flakes", "Ff", "Flakes"]
FISH_BOWL_NAMES = ["Fish Bowl", "Bowl", "Fb"]
SMALL_TANK_NAMES = ["Small Tank", "Small", "St"]
MEDIUM_TANK_NAMES = ["Medium Tank", "Medium", "Mt"]
PLANT_LIFE_NAMES = ["Plant Life", "Pl", "Plant"]

EMOJI_RARITIES = {
    "common": {
        "clownfish": "<:clownfish:849777027174760448>", "goldfish": "<:goldfish:849777027258515456>", "tiger_barb": "<:tiger_barb:849777027413311508>", "royal_blue_betta": "<:royal_blue_betta:849777027472031764>", "pufferfish": "<:pufferfish:849777027501522954>", 
        "oscar_cichlid": "<:oscar_cichlid:849777027599040522>", "neon_tetra_school": "<:neon_tetra_school:849777027326017586>", "turquoise_blue_betta": "<:turquoise_blue_betta:850970562469691433>", "tuna": "<:tuna:850970699359322122>", "squid": "<:squid:850970655695568906>",
        "shrimp": "<:shrimp:850970552830787624>", "red_betta": "<:red_betta:850970531216752660>", "paradise_fish": "<:paradise_fish:850970512695361546>", "koi": "<:koi:850970638599323678>", "headshield_slug": "<:headshield_slug:850970724231544833>",
        "guppies": "<:guppies:850970478884814908>", "electric_blue_hap": "<:electric_blue_hap:850970439136182293>", "cowfish": "<:cowfish:850970605276102658>", "clown_triggerfish": "<:clown_triggerfish:850970691628695562>", "angelfish": "<:angelfish:850970572569706526>",
        "pineapple_betta": "<:pineapple_betta:850970524414509056>", "harlequin_rasboras": "<:harlequin_rasboras:850970500686938112>", "electric_yellow_lab": "<:electric_yellow_lab:850970446648311828>", "catfish": "<:catfish:850970683718893578>",
        "blue_maomao": "<:blue_maomao:850970598784237568>", "blue_diamond_discus": "<:blue_diamond_discus:850970583499538464>", "black_orchid_betta": "<:black_orchid_betta:850970430487527486>", "banggai_cardinalfish": "<:banggai_cardinalfish:850970420869070868>",
        "bottlenose_dolphin": "<:bottlenose_dolphin:850970711634739210>", "starfish": "<:starfish:850970666986766354>"
        },
    "uncommon": {
        "flowerhorn_cichlid": "<:flowerhorn_cichlid:849777027472293918>", "lionfish": "<:lionfish:849777027765633024>", "sea_bunny": "<:sea_bunny:850970830569209887>", "manta_ray": "<:manta_ray:850970787569860658>", "surge_wrasse": "<:surge_wrasse:850970772633550858>",
        "smalltooth_swordfish": "<:smalltooth_swordfish:850970859983470623>", "seal": "<:seal:850970851435479091>", "seahorse": "<:seahorse:850970763065688074>", "quoyi_parrotfish": "<:quoyi_parrotfish:850970754002845736>", "narwhal": "<:narwhal:850970796252069888>",
        "dumbo_octopus": "<:dumbo_octopus:850977726265163776>"
        },
    "rare": {
        "axolotl": "<:axolotl:850080397450149888>", "blobfish": "<:blobfish:850970966736764939>", "cuttlefish": "<:cuttlefish:850971019078664232>", "starfish_with_pants": "<:starfish_with_pants:850977707134025758>", "bobtail_squid": "<:bobtail_squid:850977717737619478>"
        },
    "epic": {
        "asian_arowana": "<:asian_arowana:850080397350010930>", "boesemani_rainbowfish": "<:boesemani_rainbowfish:850970734028914708>"
        },
    "legendary": {
        "anglerfish": "<:anglerfish:849777027769696297>"
        },
    "mythic": {
        "mandarinfish": "<:mandarinfish:850080397081182269>"
        }
}

async def check_price(user_id: int, cost: int, bot) -> bool:
    """
    Returns if a user_id has enough money based on the cost.
    """
    async with bot.DatabaseConnection() as db:
        user_rows = await db(
            """SELECT balance FROM user_balance WHERE user_id=$1""",
            user_id,
        )
        user_balance = user_rows[0]['balance']
    return user_balance >= cost

async def buying_singular(ctx, item: str, bot):
    """
    For Buying a singular item such as a tank or theme
    """
    # Variables for possible inputs
    tanks = ["Fish Bowl", "Small Tank", "Medium Tank"]
    themes = ["Plant Life"]

    # Gets the tank info for user
    async with bot.DatabaseConnection() as db:
        tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id=$1""", ctx.author.id)
    
    # Tank slot/name info variables
    tank_slot = 0
    nonavailable_slots = []
    available_slots = []
    nonavailable_tank_types = []
    tank_names = []
    tank_size_values = {"Fish Bowl": 1, "Small Tank": 5, "Medium Tank": 25}

    # Finds the slots and names of tanks and puts them where they need to be in the list
    for type in tanks:
        if item == type:
            break
        nonavailable_tank_types.append(type)
    for tank_named in tank_row[0]['tank_name']:
        tank_slot += 1
        if tank_row[0]['tank_type'][tank_slot-1] == "":
            tank_names.append("none")
        tank_names.append(tank_named)
        if tank_named:
            if tank_row[0]['tank_type'][tank_slot-1] not in nonavailable_tank_types:
                continue
            nonavailable_slots.append(str(tank_slot))
            continue
        available_slots.append(str(tank_slot))
    
    # If the item is a tank...
    if item in tanks:

        # Asks the user what slot to put the tank in and checks that its a slot
        await ctx.send(f"What tank slot would you like to put this tank in? (Available slots: {', '.join(available_slots)}, Taken spots to be updated: {', '.join(nonavailable_slots)})")
        check = lambda slot: slot.author == ctx.author and slot.channel == ctx.channel and slot.content in available_slots or slot.content in nonavailable_slots
        try:
            message_given = await ctx.bot.wait_for("message", timeout=60.0, check=check)
            message = message_given.content
            await ctx.send(f"You have put your new tank in tank slot {message}!")
        except asyncio.TimeoutError:
            await ctx.send("Timed out asking for tank slot, no available slots given.")
            return False
        
        # Checks if it is creating a brand new tank
        if message in available_slots:

            # Asks what to name the new tank and makes sure it matches the check
            await ctx.send(f"What would you like to name this tank? (must be a different name from your other tanks, less than 32 characters, and cannot be \"none\")")
            check = lambda namem: namem.author == ctx.author and namem.channel == ctx.channel and len(namem.content) > 1 and len(namem.content) <= 32 and namem.content not in tank_names and namem.content != "none"
            try:
                name_given = await ctx.bot.wait_for("message", timeout=60.0, check=check)
                name = name_given.content
                await ctx.send(f"You have named your new tank {name}!")
            except asyncio.TimeoutError:
                await ctx.send("Timed out asking for tank name, no available name given.")
                return False
            
            # Adds the tank to the users tanks
            async with bot.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank[$1] = TRUE, tank_type[$1] = $2, tank_name[$1]=$3, fish_room[$1]=$4, tank_theme[$1]='Aqua' WHERE user_id=$5""", int(message), item, name, tank_size_values[item], ctx.author.id)
        else:

            # If the tank is just updating a tank, updates the tank
            await ctx.send(f"Tank {tank_names[int(message)-1]} has been updated to {item}!")
            async with bot.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank_type[$1] = $2, fish_room[$1]=fish_room[$1]+$3 WHERE user_id=$4 AND tank_name[$1]=$5""", int(message), item, int(tank_size_values[item] - tank_size_values[tank_row[0]['tank_type'][int(message)-1]]), ctx.author.id, tank_names[int(message)-1])
    
    # If the item is a theme...
    elif item in themes:

        # Asks for the name of the tank the user is putting the theme on and makes sure it is correct
        await ctx.send(f"What tank name would you like to put this theme on? (Available names: {', '.join(tank_names)})")
        check = lambda themem: themem.author == ctx.author and themem.channel == ctx.channel and themem.content in tank_names and themem.content != "none"
        try:
            theme_message_given = await ctx.bot.wait_for("message", timeout=60.0, check=check)
            theme_message = theme_message_given.content
            await ctx.send(f"You have put your new theme on your tank named {theme_message}!")
        except asyncio.TimeoutError:
            await ctx.send("Timed out asking for tank name, no available name given.")
            return False
        async with bot.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank_theme[$1] = $2 WHERE user_id=$3""", tank_names.index(theme_message), item.replace(" ", "_"), ctx.author.id)

class Shop(vbu.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @vbu.command(aliases=["s"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx: commands.Context):
        """
        `a.shop` This command shows everything buyable in the shop, along with their prices.
        """

        await ctx.send(embed=FISH_SHOP_EMBED)

    @vbu.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx: commands.Context, item: typing.Optional[str], amount: typing.Optional[int] = 1):
        """
        `a.buy \"item\" \"amount(optional)\"` This command buys an item from a shop, with the given value (default one, tanks and themes are always one).
        """

        # Say what's valid
        all_names = [
            COMMON_BAG_NAMES, UNCOMMON_BAG_NAMES, RARE_BAG_NAMES, EPIC_BAG_NAMES,
            LEGENDARY_BAG_NAMES, MYSTERY_BAG_NAMES, FISH_FLAKES_NAMES, FISH_BOWL_NAMES, SMALL_TANK_NAMES, MEDIUM_TANK_NAMES, PLANT_LIFE_NAMES
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
            "cfb": (COMMON_BAG_NAMES, 50, "Common Fish Bag", inventory_insert_sql.format("cfb")),
            "ufb": (UNCOMMON_BAG_NAMES, 100, "Uncommon Fish Bag", inventory_insert_sql.format("ufb")),
            "rfb": (RARE_BAG_NAMES, 200, "Rare Fish Bag", inventory_insert_sql.format("rfb")),
            "efb": (EPIC_BAG_NAMES, 400, "Epic Fish Bag", inventory_insert_sql.format("efb")),
            "lfb": (LEGENDARY_BAG_NAMES, 500, "Legendary Fish Bag", inventory_insert_sql.format("lfb")),
            "mfb": (MYSTERY_BAG_NAMES, 250),
            "flakes": (FISH_FLAKES_NAMES, 5, "Fish Flakes", inventory_insert_sql.format("flakes")),
            "Fish Bowl": (FISH_BOWL_NAMES, 100, "Fish Bowl", ""),
            "Small Tank": (SMALL_TANK_NAMES, 500, "Small Tank", ""),
            "Medium Tank": (MEDIUM_TANK_NAMES, 2500, "Medium Tank", ""),
            "Plant Life": (PLANT_LIFE_NAMES, 1000, "Plant Life", "")
        }
        item_name_singular = [
            FISH_BOWL_NAMES, SMALL_TANK_NAMES, MEDIUM_TANK_NAMES, PLANT_LIFE_NAMES
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
            if item.title in item_name_singular:
                amount = 1
            # See if the user has enough money
            full_cost = cost * amount
            if not await check_price(ctx.author.id, full_cost, bot = self.bot):
                return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:852057443503964201> for this!")

            # here
            check = False
            # Add item to user, check if item is a singular item and if so runs that function
            for item_names in item_name_singular:
                if item.title() in item_names:
                    check = True
            print(check)
            if check == True:
                print("yes")
                if await buying_singular(ctx, str(response), bot = self.bot) == False:
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
        await ctx.send(f"You bought {amount:,} {response} for {full_cost:,} Sand Dollars <:sand_dollar:852057443503964201>!")

    @vbu.command(aliases=["u"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx:commands.Context, item: str):
        """
        `a.use \"item\"` This command is only for using fish bags, using a fish bag is just like using the fish command.
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
            new_fish = self.bot.get_cog("Fishing").make_inverted(new_fish)
        elif special == "golden":
            new_fish = self.bot.get_cog("Fishing").make_golden(new_fish)

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
        embed.color = self.bot.get_cog("Fishing").RARITY_CULERS[rarity]
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)

        # Ask the user if they want to sell the fish
        await self.bot.get_cog("Fishing").ask_to_sell_fish(ctx.author, message, new_fish)

    @vbu.command(aliases=["inv"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def inventory(self, ctx:commands.Context):
        """
        `a.inventory` Shows your bag inventory.
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
            embed.add_field(name=f'{name}s',value=fetched_info[count], inline=True)
            count += 1
        await ctx.send(embed=embed)
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def slots(self, ctx: commands.Context):
        """
        `a.slots` This command roles the slots, which costs **5** sand dollars and can win you a fish.
        """

        # See if the user has enough money
        if not await check_price(ctx.author.id, 5, bot = self.bot):
            return await ctx.send("You don't have enough money for this! (5)")

        # Remove money from the user
        async with self.bot.database() as db:
            await db("""UPDATE user_balance SET balance=balance-5 WHERE user_id = $1""", ctx.author.id)

        # Chooses the random fish for nonwinning rows
        chosen_fish = []
        rarities_of_fish = []
        for i in range(9):
            rarity_random = random.choices(*self.bot.get_cog("Fishing").rarity_percentage_finder(1))[0]
            new_fish = random.choice(list(utils.EMOJI_RARITIES[rarity_random]))
            rarities_of_fish.append(rarity_random)
            chosen_fish.append(new_fish)
        
        # Chooses winning fish
        rarity = random.choices(*self.bot.get_cog("Fishing").rarity_percentage_finder(1))[0]
        fish_type = random.choice(list(EMOJI_RARITIES[rarity]))
        emoji_id = EMOJI_RARITIES[rarity][fish_type]

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
                row.append(f"{EMOJI_RARITIES[rarities_of_fish[i]][chosen_fish[i]]}"
                f"{EMOJI_RARITIES[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                f"{EMOJI_RARITIES[rarities_of_fish[i+2]][chosen_fish[i+2]]}")
            row.append(f"{emoji_id}{emoji_id}{emoji_id}")
            embed.add_field(name="*spent 5 Sand Dollars <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Lucky", value=f"You won {fish_random_name.title()} :)", inline=False)
            message = await ctx.send(embed=embed)
            await self.bot.get_cog("Fishing").ask_to_sell_fish(ctx.author, message, used_fish)
        else:
            for i in range(0, 9, 3):
                row.append(f"{EMOJI_RARITIES[rarities_of_fish[i]][chosen_fish[i]]}"
                f"{EMOJI_RARITIES[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                f"{EMOJI_RARITIES[rarities_of_fish[i+2]][chosen_fish[i+2]]}")
            embed.add_field(name="*spent 5 Sand Dollars <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Unlucky", value="You lost :(")
            await ctx.send(embed=embed)

    @vbu.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx: commands.Context, user: typing.Optional[discord.Member]):
        """
        `a.balance \"user(optional)\"` This command checks your balance or another users.
    
        """

        async with self.bot.database() as db:
            if user:
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user.id)
                return await ctx.send(f"{user.display_name} has {fetched[0]['balance']} Sand Dollars <:sand_dollar:852057443503964201>!" if fetched else f"{user.display_name} has no Sand Dollars <:sand_dollar:852057443503964201>!")

            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            return await ctx.send(f"You have {fetched[0]['balance']} Sand Dollars!" if fetched else "You have no Sand Dollars <:sand_dollar:852057443503964201>!")
 
def setup(bot):
    bot.add_cog(Shop(bot))
