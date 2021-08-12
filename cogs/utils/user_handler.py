import discord
import asyncio
import math
import random

from cogs import utils

async def ask_to_sell_fish(bot, user: discord.User, message: discord.Message, new_fish: dict):
    """
    Ask the user if they want to sell a fish they've been given.
    """

    # Add the emojis to the message
    emojis = [844594468580491264, 844594478392147968]
    for i in emojis:
        await message.add_reaction(bot.get_emoji(i))

    # See what reaction the user is adding to the message
    check = lambda reaction, reactor: reaction.emoji.id in emojis and reactor.id == user.id and reaction.message.id == message.id
    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        choice = "sell" if reaction.emoji.id == 844594478392147968 else "keep"
    except asyncio.TimeoutError:
        await message.channel.send("Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
        choice = "sell"

    async with bot.database() as db:
        fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id=$1""", user.id)
        upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", user.id)
        if not upgrades:
            await db("""INSERT INTO user_upgrades (user_id) VALUES ($1)""", user.id)
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", user.id)

    # See if they want to sell the fish
    if choice == "sell":
        sell_multipliers = { 1: 1.0, 2: 1.1, 3: 1.3, 4: 1.6, 5: 2.0}
        money_earned = math.floor(int(new_fish['cost']) * sell_multipliers[upgrades[0]['rod_upgrade']])
        async with bot.database() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                user.id, money_earned,
            )
        await message.channel.send(f"Sold your **{new_fish['name']}** for **{money_earned}** Sand Dollars <:sand_dollar:852057443503964201>!")
        return

    # Get their current fish names
    fish_names = []

    fish_names = [i['fish_name'] for i in fish_rows]
    fish_list = [(i['fish_name'], i['fish']) for i in fish_rows]
    fish_list = sorted(fish_list, key=lambda x: x[1])
    levels_start = {1: (1,2), 2: (2,4), 3: (3,6), 4: (4,8), 5: (5,10)}
    level = random.randint(levels_start[upgrades[0]['weight_upgrade']][0], levels_start[upgrades[0]['weight_upgrade']][1])
    xp_max = math.floor(25 * level ** 1.5)
    sorted_fish = {
        "common": [],
        "uncommon": [],
        "rare": [],
        "epic": [],
        "legendary": [],
        "mythic": []
    }

    # Sorted Fish will become a dictionary of {rarity: [list of fish names of fish in that category]} if the fish is in the user's inventory
    for rarity, fish_types in bot.fish.items():  # For each rarity level
        for _, fish_detail in fish_types.items():  # For each fish in that level
            raw_name = fish_detail["raw_name"]
            for user_fish_name, user_fish in fish_list:
                if raw_name == utils.get_normal_name(user_fish):  # If the fish in the user's list matches the name of a fish in the rarity catgeory
                    sorted_fish[rarity].append((user_fish_name, user_fish))  # Append to the dictionary

    # They want to keep - ask what they want to name the fish
    await message.channel.send("What do you want to name your new fish? (32 character limit and cannot be named the same as another fish you own)")
    check = lambda m: m.author == user and m.channel == message.channel and len(m.content) > 1 and len(m.content) <= 32 and m.content not in fish_names
    try:
        name_message = await bot.wait_for("message", timeout=60.0, check=check)
        name = name_message.content
        await message.channel.send(f"Your new fish **{name}** (Lvl. {level}) has been added to your bucket!")
    except asyncio.TimeoutError:
        name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
        await message.channel.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}** (Lvl. {level})")

    # Save the fish name
    async with bot.database() as db:
        await db(
            """INSERT INTO user_fish_inventory (user_id, fish, fish_name, fish_size, fish_level, fish_xp_max) VALUES ($1, $2, $3, $4, $5, $6)""",
            user.id, new_fish["raw_name"], name, new_fish["size"], level, xp_max
        )

async def check_price(bot, user_id: int, cost: int) -> bool:
    """
    Returns if a user_id has enough money based on the cost.
    """
    async with bot.database() as db:
        user_rows = await db(
            """SELECT balance FROM user_balance WHERE user_id=$1""",
            user_id,
        )
        user_balance = user_rows[0]['balance']
    return user_balance >= cost

async def buying_singular(bot, ctx, item: str):
    """
    For Buying a singular item such as a tank or theme
    """
    # Variables for possible inputs
    tanks = ["Fish Bowl", "Small Tank", "Medium Tank"]
    themes = ["Plant Life"]

    # Gets the tank info for user
    async with bot.database() as db:
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
            async with bot.database() as db:
                await db("""UPDATE user_tank_inventory SET tank[$1] = TRUE, tank_type[$1] = $2, tank_name[$1]=$3, fish_room[$1]=$4, tank_theme[$1]='Aqua' WHERE user_id=$5""", int(message), item, name, tank_size_values[item], ctx.author.id)
        else:

            # If the tank is just updating a tank, updates the tank
            await ctx.send(f"Tank {tank_names[int(message)-1]} has been updated to {item}!")
            async with bot.database() as db:
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
        async with bot.database() as db:
                await db("""UPDATE user_tank_inventory SET tank_theme[$1] = $2 WHERE user_id=$3""", tank_names.index(theme_message), item.replace(" ", "_"), ctx.author.id)

