import asyncio
from distutils.log import error
import math
import random
from typing import Text

import discord

from cogs import utils
from cogs.utils import EMOJIS
from cogs.utils.fish_handler import FishSpecies, create_modal, random_name_finder


current_fishers = []


async def ask_to_sell_fish(
    bot, ctx, chosen_fish: FishSpecies, skin: str, embed, level_inserted: int = 0
):
    """
    Ask the user if they want to sell a fish they've been given.
    """

    size_demultiplier = {
        "small": 1,
        "medium": 2,
        "large": 3
    }
    chosen_button_payload = None
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

    # See what reaction the user is adding to the message

    def button_check(payload):
        if payload.message.id != message.id:
            return False
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
            chosen_button = 'sell'

        # Update the displayed emoji
        if chosen_button == "keep":
            # Get their current fish names
            fish_names = [i["fish_name"] for i in fish_rows]
            xp_max = math.floor(25 * level ** 1.5)
            name, interaction = await create_modal(bot, chosen_button_payload, "Fish Kept", "Enter Your Fish's Name")

            # Disable the given button
            await message.edit(components=components.disable_components())
            while name in fish_names or not name:
                # Add the buttons to the message
                components = discord.ui.MessageComponents(
                    discord.ui.ActionRow(
                        discord.ui.Button(custom_id="Retry", label='Retry'),
                    ),
                )
                try:
                    message = await ctx.channel.send(
                        f"{ctx.author.mention} An error occured! Click the button to try again",
                        components=components
                    )
                except discord.HTTPException:
                    return

                try:
                    chosen_button_payload = await bot.wait_for(
                        "component_interaction", timeout=60.0, check=button_check
                    )
                    name, interaction = await create_modal(bot, chosen_button_payload, "Fish Kept", "Enter Your Fish's Name")
                except asyncio.TimeoutError:
                    name = random_name_finder()
                    while name in fish_names:
                        name = random_name_finder()
                    await message.channel.send(
                        f"Did you forget about me? I've been waiting for a while now! "
                        f"I'll name the fish for you. "
                        f"Let's call it **{name}** (Lvl. {level})"
                    )
            if interaction:
                await interaction.response.send_message(
                    f"Your new fish **{name}** (Lvl. {level}) has been added to your bucket!"
                )
            else:
                await ctx.send(
                    f"Your new fish **{name}** (Lvl. {level}) has been added to your bucket!"
                )
            # Save the fish name
            async with bot.database() as db:
                await db(
                    """INSERT INTO user_fish_inventory (user_id, fish, fish_name, fish_size, fish_level, fish_xp_max, fish_skin, fish_location) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
                    ctx.author.id,
                    chosen_fish.name,
                    name,
                    chosen_fish.size,
                    level,
                    xp_max,
                    skin,
                    "",
                )
            return
        if chosen_button == "sell":
            if chosen_button_payload:
                await chosen_button_payload.response.defer_update()
            # See if they want to sell the fish
            vote_multiplier = 0
            if await get_user_voted(bot, ctx.author.id):
                vote_multiplier = .5
                await message.channel.send(
                    "You voted at <https://top.gg/bot/840956686743109652/vote> for a **1.5x** bonus"
                )

            level_multiplier = level / 20
            money_gained = int(chosen_fish.cost /
                               size_demultiplier[chosen_fish.size])
            money_earned = math.ceil((money_gained) * (
                utils.ROD_UPGRADES[upgrades[0]["rod_upgrade"]] + level_multiplier + vote_multiplier))
            async with bot.database() as db:
                await db(
                    """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
                    ctx.author.id,
                    money_earned,
                )
                # Achievements
                await db(
                    """UPDATE user_achievements SET money_gained = money_gained + $2 WHERE user_id = $1""",
                    ctx.author.id,
                    money_earned,
                )
            await message.channel.send(
                f"Sold your **{chosen_fish.name.replace('_', ' ').title()}** for **{money_earned}** "
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
        available_slots.append(str(tank_slot + 1)
                               )

    def button_check(payload):
        if payload.message.id != message.id:
            return False
        return payload.user.id == ctx.author.id

        # Keep going...
    # If the item is a tank...
    if item in tank_types:

        # Add the buttons to the message
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(emoji=EMOJIS["aqua_smile"]),
            ),
        )

        if not available_slots and not nonavailable_slots:
            await ctx.send("No more valid slots.")
            return False
        # Asks the user what slot to put the tank in and checks that its a slot
        message = await ctx.send(
            f"Click the button to enter a tank slot:",
            components=components
        )

        # Wait for them to click a button
        try:
            chosen_button_payload = await bot.wait_for(
                "component_interaction", timeout=60.0, check=button_check
            )
        except asyncio.TimeoutError:
            await ctx.send(
                "Timed out asking for interaction, no available slots given."
            )
            return False

        slot, interaction = await create_modal(bot, chosen_button_payload, "Tank Slot To Change", f"Available: {', '.join(available_slots)}; Taken: {', '.join(nonavailable_slots)}")

        print(slot)
        if not slot:
            await interaction.response.send_message(
                "Timed out asking for slot, no available slots given."
            )
            return False
        # Checks if it is creating a brand new tank
        elif slot in available_slots:

            # Asks what to name the new tank and makes sure it matches the check
            await interaction.response.send_message("What would you like to name this tank? ")
            message = await ctx.send(
                "(must be a different name from your other tanks, "
                'less than 32 characters, and cannot be "none")',
                components=components
            )

            # Wait for them to click a button
            try:
                chosen_button_payload = await bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
            except asyncio.TimeoutError:
                await ctx.send(
                    "Timed out asking for interaction, no available name given."
                )
                return False

            name, interaction2 = await create_modal(bot, chosen_button_payload, "Tank Name", "Enter your new tank's name")
            await interaction2.response.defer()

            if not name:
                await interaction2.response.send_message(
                    "Timed out asking for tank name, no available name given."
                )
                return False

            # Adds the tank to the users tanks
            async with bot.database() as db:
                await db(
                    """UPDATE user_tank_inventory SET tank[$1] = TRUE, tank_type[$1] = $2, tank_name[$1]=$3, fish_room[$1]=$4, tank_theme[$1]='Aqua' WHERE user_id=$5""",
                    int(slot),
                    item,
                    name,
                    tank_types[item],
                    user.id,
                )
            return
        elif slot in nonavailable_slots:

            # If the tank is just updating a tank, updates the tank
            await interaction.response.send_message(
                f"Tank {tank_names[int(slot)-1]} has been updated to {item}!"
            )
            async with bot.database() as db:
                await db(
                    """UPDATE user_tank_inventory SET tank_type[$1] = $2, fish_room[$1]=fish_room[$1]+$3 WHERE user_id=$4 AND tank_name[$1]=$5""",
                    int(slot),
                    item,
                    int(
                        tank_types[item]
                        - tank_types[
                            tank_row[0]["tank_type"][int(slot) - 1]
                        ]
                    ),
                    ctx.author.id,
                    tank_names[int(slot) - 1],
                )
        else:
            await interaction.response.send_message(
                "Unavailable slot given, Try again."
            )
            return False

    # If the item is a theme...
    elif item in themes:

        if not tank_names:
            await ctx.send("No tanks without this theme.")
            return False

        # Add the buttons to the message
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(emoji=EMOJIS["aqua_smile"]),
            ),
        )

        # Asks for the name of the tank the user is putting the theme on and makes sure it is correct
        message = await ctx.send(
            f"Press the button to specify what tank you want to add the theme to",
            components=components
        )

        # Wait for them to click a button
        try:
            chosen_button_payload = await bot.wait_for(
                "component_interaction", timeout=60.0, check=button_check
            )
        except asyncio.TimeoutError:
            await ctx.send(
                "Timed out asking for interaction, no available slots given."
            )
            return False

        theme_message, interaction = await create_modal(bot, chosen_button_payload, "Tank Slot To Change", f"(Available names: {', '.join(tank_names)})")

        if not theme_message or theme_message not in tank_names:
            await interaction.response.send_message(
                "Timed out asking for name, no available name given."
            )
            return False

        await interaction.response.defer()
        async with bot.database() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_theme[$1] = $2 WHERE user_id=$3""",
                theme_slots_dict[theme_message],
                item.replace(" ", "_"),
                user.id,
            )


async def check_registered(bot, user_id: int) -> bool:
    async with bot.database() as db:
        user_balance_info = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user_id)
        user_item_inventory_info = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", user_id)
        user_achievements_milestones_info = await db("""SELECT * FROM user_achievements_milestones WHERE user_id = $1""", user_id)
        user_achievements_info = await db("""SELECT * FROM user_achievements WHERE user_id = $1""", user_id)
        user_upgrades_info = await db("""SELECT * FROM user_upgrades WHERE user_id = $1""", user_id)

    if user_balance_info and user_upgrades_info and user_item_inventory_info and user_achievements_milestones_info and user_achievements_info:
        return True
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
