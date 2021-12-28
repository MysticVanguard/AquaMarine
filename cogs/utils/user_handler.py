import asyncio
import math
import random

import discord

from cogs import utils
from cogs.utils import EMOJIS


current_fishers = []


async def ask_to_sell_fish(
    bot, ctx, new_fish: dict, embed, level_inserted: int = 0
):
    """
    Ask the user if they want to sell a fish they've been given.
    """

    # Add the buttons to the message
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(custom_id="keep", emoji=EMOJIS["keep"]),
            discord.ui.Button(custom_id="sell", emoji=EMOJIS["sell"]),
        ),
    )
    try:
        message = await ctx.send(embed=embed, components=components)
    except discord.HTTPException:
        return

    async with bot.database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id=$1""",
            ctx.author.id,
        )
        upgrades = await db(
            """SELECT rod_upgrade, weight_upgrade FROM user_upgrades WHERE user_id = $1""",
            ctx.author.id,
        )
        if not upgrades:
            await db(
                """INSERT INTO user_upgrades (user_id) VALUES ($1)""",
                ctx.author.id,
            )
            upgrades = await db(
                """SELECT rod_upgrade, weight_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

    # See what reaction the user is adding to the message

    def button_check(payload):
        if payload.message.id != message.id:
            return False
        bot.loop.create_task(payload.response.defer_update())
        return payload.user.id == ctx.author.id
        # Keep going...

    # Level variables
    level = (
        random.randint(
            utils.WEIGHT_UPGRADES[upgrades[0]["weight_upgrade"]][0],
            utils.WEIGHT_UPGRADES[upgrades[0]["weight_upgrade"]][1],
        )
        + level_inserted
    )

    while True:

        # Wait for them to click a button
        try:
            chosen_button_payload = await bot.wait_for(
                "component_interaction", timeout=60.0, check=button_check
            )
            chosen_button = chosen_button_payload.component.custom_id.lower()
        except asyncio.TimeoutError:
            await message.edit(components=components.disable_components())
            await message.channel.send(
                "Did you forget about me? I've been waiting for a while now! "
                "I'll just assume you wanted to sell the fish."
            )
            # See if they want to sell the fish
            vote_multiplier = 1
            if await get_user_voted(bot, ctx.author.id):
                vote_multiplier = 1.5
                await message.channel.send(
                    "You voted at <https://top.gg/bot/840956686743109652/vote> for a **1.5x** bonus"
                )

            level_multiplier = level / 20
            money_earned = math.ceil(
                (int(new_fish["cost"]))
                * utils.ROD_UPGRADES[upgrades[0]["rod_upgrade"]]
                * (1 + level_multiplier)
                * vote_multiplier
            )

            async with bot.database() as db:
                await db(
                    """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                    ctx.author.id,
                    money_earned,
                )
                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + $2""",
                    ctx.author.id,
                    money_earned,
                )
            await message.channel.send(
                f"Sold your **{new_fish['name']}** for **{money_earned}** "
                f"{EMOJIS['sand_dollar']}!"
            )
            # Disable the given button
            await message.edit(components=components.disable_components())
            return

        # Update the displayed emoji
        if chosen_button == "keep":
            # Disable the given button
            await message.edit(components=components.disable_components())
            # Get their current fish names
            fish_names = [i["fish_name"] for i in fish_rows]
            fish_list = [(i["fish_name"], i["fish"]) for i in fish_rows]
            fish_list = sorted(fish_list, key=lambda x: x[1])
            xp_max = math.floor(25 * level ** 1.5)
            sorted_fish = {
                "common": [],
                "uncommon": [],
                "rare": [],
                "epic": [],
                "legendary": [],
                "mythic": [],
            }

            # Sorted Fish will become a dictionary of {rarity: [list of fish names of fish in that category]} if the fish is in the user's inventory
            for rarity, fish_types in bot.fish.items():
                for _, fish_detail in fish_types.items():
                    raw_name = fish_detail["raw_name"]
                    for user_fish_name, user_fish in fish_list:
                        # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        if raw_name == utils.get_normal_name(user_fish):
                            # Append to the dictionary
                            sorted_fish[rarity].append(
                                (user_fish_name, user_fish)
                            )

            # They want to keep - ask what they want to name the fish
            await message.channel.send(
                "What do you want to name your new fish? (32 character limit and cannot be named the same as another fish you own)"
            )

            def message_check(msg):
                return (
                    msg.author == ctx.author
                    and msg.channel.id == message.channel.id
                    and len(msg.content) > 1
                    and len(msg.content) <= 32
                    and msg.content not in fish_names
                )

            try:
                name_message = await bot.wait_for(
                    "message", timeout=60.0, check=message_check
                )
                name = name_message.content
                await message.channel.send(
                    f"Your new fish **{name}** (Lvl. {level}) has been added to your bucket!"
                )
            except asyncio.TimeoutError:
                titles = [
                    "Captain",
                    "Mr.",
                    "Mrs.",
                    "Commander",
                    "Sir",
                    "Madam",
                    "Skipper",
                    "Crewmate",
                ]
                names = [
                    "Nemo",
                    "Bubbles",
                    "Jack",
                    "Finley",
                    "Coral",
                    "Fish",
                    "Turtle",
                    "Squid",
                    "Sponge",
                    "Starfish",
                ]
                name = f"{random.choice(titles)} {random.choice(names)}"
                while name in fish_names:
                    name = f"{random.choice(titles)} {random.choice(names)}"
                await message.channel.send(
                    f"Did you forget about me? I've been waiting for a while now! "
                    f"I'll name the fish for you. "
                    f"Let's call it **{name}** (Lvl. {level})"
                )

            # Save the fish name
            async with bot.database() as db:
                await db(
                    """INSERT INTO user_fish_inventory (user_id, fish, fish_name, fish_size, fish_level, fish_xp_max) VALUES ($1, $2, $3, $4, $5, $6)""",
                    ctx.author.id,
                    new_fish["raw_name"],
                    name,
                    new_fish["size"],
                    level,
                    xp_max,
                )
            return
        if chosen_button == "sell":
            # See if they want to sell the fish
            vote_multiplier = 1
            if await get_user_voted(bot, ctx.author.id):
                vote_multiplier = 1.5
                await message.channel.send(
                    "You voted at <https://top.gg/bot/840956686743109652/vote> for a **1.5x** bonus"
                )

            level_multiplier = level / 20
            money_earned = math.ceil(
                (int(new_fish["cost"]))
                * utils.ROD_UPGRADES[upgrades[0]["rod_upgrade"]]
                * (1 + level_multiplier)
                * vote_multiplier
            )
            async with bot.database() as db:
                await db(
                    """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                    ctx.author.id,
                    money_earned,
                )
                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + $2""",
                    ctx.author.id,
                    money_earned,
                )
            await message.channel.send(
                f"Sold your **{new_fish['name']}** for **{money_earned}** "
                f"{EMOJIS['sand_dollar']}!"
            )
            # Disable the given button
            await message.edit(components=components.disable_components())
            return


async def check_price(bot, user_id: int, cost: int, balance_type: str) -> bool:
    """
    Returns if a user_id has enough money based on the cost.
    """

    async with bot.database() as db:
        user_rows = await db(
            f"""SELECT {balance_type} FROM user_balance WHERE user_id=$1""",
            user_id,
        )
        if user_rows:
            user_balance = user_rows[0][balance_type]
        else:
            user_balance = 0
    return user_balance >= cost


async def buying_singular(bot, user: discord.user, ctx, item: str):
    """
    For Buying a singular item such as a tank or theme.
    """

    # Variables for possible inputs
    themes = ["Plant Life"]

    # Gets the tank info for user
    async with bot.database() as db:
        tank_row = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id=$1""", user.id
        )
        if not tank_row:
            await ctx.send("Get your starter tank first with `firsttank`!")
            return False

    # Tank slot/name info variables
    nonavailable_slots = []
    available_slots = []
    theme_slots_dict = {}
    nonavailable_tank_types = []
    tank_names = []
    tank_types = {"Fish Bowl": 1, "Small Tank": 5, "Medium Tank": 25}

    # Finds the slots and names of tanks and puts them where they need to be in the list
    for tank_type in tank_types:
        if item == tank_type:
            break
        nonavailable_tank_types.append(tank_type)

    for tank_slot, tank_name in enumerate(tank_row[0]["tank_name"]):
        theme_slots_dict[tank_name] = tank_slot
        if not tank_row[0]["tank_type"][tank_slot]:
            tank_names.append("none")
        if tank_row[0]["tank_theme"][tank_slot] != item.replace(" ", "_"):
            tank_names.append(tank_name)
        if tank_name:
            if tank_row[0]["tank_type"][tank_slot] in nonavailable_tank_types:
                nonavailable_slots.append(str(tank_slot + 1))
            continue
        available_slots.append(str(tank_slot + 1))

    # If the item is a tank...
    if item in tank_types:

        # Asks the user what slot to put the tank in and checks that its a slot
        await ctx.send(
            f"What tank slot would you like to put this tank in? "
            f"(Available slots: {', '.join(available_slots)}, "
            f"Taken spots to be updated: {', '.join(nonavailable_slots)})"
        )

        def slot_check(slot):
            return (
                slot.author == ctx.author
                and slot.channel == ctx.channel
                and slot.content in available_slots
                or slot.content in nonavailable_slots
            )

        try:
            message_given = await ctx.bot.wait_for(
                "message", timeout=60.0, check=slot_check
            )
            message = message_given.content
            await ctx.send(
                f"You have put your new tank in tank slot {message}!"
            )
        except asyncio.TimeoutError:
            await ctx.send(
                "Timed out asking for tank slot, no available slots given."
            )
            return False

        # Checks if it is creating a brand new tank
        if message in available_slots:

            # Asks what to name the new tank and makes sure it matches the check
            await ctx.send(
                "What would you like to name this tank? "
                "(must be a different name from your other tanks, "
                'less than 32 characters, and cannot be "none")'
            )

            def name_check(namem):
                return (
                    namem.author == ctx.author
                    and namem.channel == ctx.channel
                    and len(namem.content) > 1
                    and len(namem.content) <= 32
                    and namem.content not in tank_names
                    and namem.content != "none"
                )

            try:
                name_given = await ctx.bot.wait_for(
                    "message", timeout=60.0, check=name_check
                )
                name = name_given.content
                await ctx.send(f"You have named your new tank {name}!")
            except asyncio.TimeoutError:
                await ctx.send(
                    "Timed out asking for tank name, no available name given."
                )
                return False

            # Adds the tank to the users tanks
            async with bot.database() as db:
                await db(
                    """UPDATE user_tank_inventory SET tank[$1] = TRUE, tank_type[$1] = $2, tank_name[$1]=$3, fish_room[$1]=$4, tank_theme[$1]='Aqua' WHERE user_id=$5""",
                    int(message),
                    item,
                    name,
                    tank_types[item],
                    user.id,
                )
        else:

            # If the tank is just updating a tank, updates the tank
            await ctx.send(
                f"Tank {tank_names[int(message)-1]} has been updated to {item}!"
            )
            async with bot.database() as db:
                await db(
                    """UPDATE user_tank_inventory SET tank_type[$1] = $2, fish_room[$1]=fish_room[$1]+$3 WHERE user_id=$4 AND tank_name[$1]=$5""",
                    int(message),
                    item,
                    int(
                        tank_types[item]
                        - tank_types[
                            tank_row[0]["tank_type"][int(message) - 1]
                        ]
                    ),
                    ctx.author.id,
                    tank_names[int(message) - 1],
                )

    # If the item is a theme...
    elif item in themes:

        # Asks for the name of the tank the user is putting the theme on and makes sure it is correct
        await ctx.send(
            f"What tank name would you like to put this theme on? "
            f"(Available names: {', '.join(tank_names)})"
        )

        def theme_check(themem):
            return (
                themem.author == ctx.author
                and themem.channel == ctx.channel
                and themem.content in tank_names
                and themem.content != "none"
            )

        try:
            theme_message_given = await ctx.bot.wait_for(
                "message", timeout=60.0, check=theme_check
            )
            theme_message = theme_message_given.content
            await ctx.send(
                f"You have put your new theme on your tank named {theme_message}!"
            )
        except asyncio.TimeoutError:
            await ctx.send(
                "Timed out asking for tank name, no available name given."
            )
            return False

        async with bot.database() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_theme[$1] = $2 WHERE user_id=$3""",
                theme_slots_dict[theme_message],
                item.replace(" ", "_"),
                user.id,
            )


# Vote confirmer from https://github.com/Voxel-Fox-Ltd/Flower/blob/master/cogs/plant_care_commands.py
async def get_user_voted(bot, user_id: int) -> bool:
    """
    Determines whether or not a user has voted for the bot on Top.gg.
    Args:
        user_id (int): The ID of the user we want to check
    Returns:
        bool: Whether or not the user voted for the bot
    """

    topgg_token = bot.config.get("bot_listing_api_keys", {}).get("topgg_token")
    if not topgg_token:
        return False
    params = {"userId": user_id}
    headers = {"Authorization": topgg_token}
    bot_client_id = bot.config["oauth"]["client_id"]
    url = f"https://top.gg/api/bots/{bot_client_id}/check"

    async with bot.session.get(url, params=params, headers=headers) as ret:
        try:
            data = await ret.json()
        except Exception:
            return False
        if ret.status != 200:
            return False
    return bool(data["voted"])
