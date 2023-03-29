import asyncio
import discord
from discord.ext import vbu
from cogs import utils
from typing import Tuple, List


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
                discord.ui.Button(emoji=utils.EMOJIS["aqua_smile"]),
            ),
        )

        if not available_slots and not nonavailable_slots:
            await ctx.send("No more valid slots.")
            return False
        # Asks the user what slot to put the tank in and checks that its a slot
        message = await ctx.send(
            f"Click the button to enter a tank slot:", components=components
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

        slot, interaction = await utils.create_modal(
            bot,
            chosen_button_payload,
            "Tank Slot To Change",
            f"Available: {', '.join(available_slots)}; Taken: {', '.join(nonavailable_slots)}",
        )

        if not slot:
            await interaction.response.send_message(
                "Timed out asking for slot, no available slots given."
            )
            return False
        # Checks if it is creating a brand new tank
        elif slot in available_slots:

            # Asks what to name the new tank and makes sure it matches the check
            await interaction.response.send_message(
                "What would you like to name this tank? "
            )
            message = await ctx.send(
                "(must be a different name from your other tanks, "
                'less than 32 characters, and cannot be "none")',
                components=components,
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

            name, interaction2 = await utils.create_modal(
                bot, chosen_button_payload, "Tank Name", "Enter your new tank's name"
            )
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
                        - tank_types[tank_row[0]["tank_type"][int(slot) - 1]]
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
                discord.ui.Button(emoji=utils.EMOJIS["aqua_smile"]),
            ),
        )

        # Asks for the name of the tank the user is putting the theme on and makes sure it is correct
        message = await ctx.send(
            f"Press the button to specify what tank you want to add the theme to",
            components=components,
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

        theme_message, interaction = await utils.create_modal(
            bot,
            chosen_button_payload,
            "Tank Slot To Change",
            f"(Available names: {', '.join(tank_names)})",
        )

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


async def check_registered(bot, ctx, user_id: int):
    async with bot.database() as db:
        user_balance_info = await db(
            """SELECT * FROM user_balance WHERE user_id = $1""", user_id
        )
        user_item_inventory_info = await db(
            """SELECT * FROM user_item_inventory WHERE user_id = $1""", user_id
        )
        user_achievements_milestones_info = await db(
            """SELECT * FROM user_achievements_milestones WHERE user_id = $1""", user_id
        )
        user_achievements_info = await db(
            """SELECT * FROM user_achievements WHERE user_id = $1""", user_id
        )
        user_upgrades_info = await db(
            """SELECT * FROM user_upgrades WHERE user_id = $1""", user_id
        )

    if (
        user_balance_info
        and user_upgrades_info
        and user_item_inventory_info
        and user_achievements_milestones_info
        and user_achievements_info
    ):
        return

    start_message = (
        f"Welcome to AquaMarine! This command helps me get you into the bot, while also displaying some information I think will prove good to have."
        f" First things first, I want to mention that there is an in-bot guide for if you get confused on anything that should be able to explain most"
        f" things, and it can be accessed with the `guide` command. If you're still confused on anything you can use the `support` command to get the"
        f" link to the support server."
    )
    await ctx.send(start_message)

    async with bot.database() as db:
        if not user_balance_info:
            await db(
                """INSERT INTO user_balance (user_id, casts) VALUES ($1, 6)""", user_id
            )
        if not user_upgrades_info:
            await db("""INSERT INTO user_upgrades (user_id) VALUES ($1)""", user_id)
        if not user_item_inventory_info:
            await db(
                """INSERT INTO user_item_inventory (user_id) VALUES ($1)""", user_id
            )
        if not user_achievements_milestones_info:
            await db(
                """INSERT INTO user_achievements_milestones (user_id) VALUES ($1)""",
                user_id,
            )
        if not user_achievements_info:
            await db("""INSERT INTO user_achievements (user_id) VALUES ($1)""", user_id)


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


async def user_item_inventory_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_item_inventory WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_fish_inventory_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_tank_inventory_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_upgrades_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_upgrades WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_balance_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_balance WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_achievements_milestones_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_achievements_milestones WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def user_achievements_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_achievements WHERE user_id = $1""",
            user_id,
        )
        return list(selected)


async def fish_pool_location_db_call() -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM fish_pool_location""",
        )
        return list(selected)


async def user_location_info_db_call(user_id: int) -> list:
    async with vbu.Database() as db:
        selected = await db(
            """SELECT * FROM user_location_info WHERE user_id = $1""",
            user_id,
        )
        return selected


ROD_UPGRADES = {0: 1, 1: 1.4, 2: 1.8, 3: 2.2, 4: 2.6, 5: 3.0}

# Bait upgrade that increases your chances of catching rarer fish
BAIT_UPGRADE = {
    0: [
        # 5   3               164/240 --> 121/240 -26.36%
        ("common", 0.6842),
        # 15  1   5           60/240  --> 84/240  +40%    2
        ("uncommon", 0.25),
        # 75      1   5       12/240  --> 24/240  +100%   1   2
        ("rare", 0.05),
        # 375         1   2   2/240   --> 8/240   +250%       1   5
        ("epic", 0.01),
        # 750             1   1/240   --> 2/240   +100%           1
        ("legendary", 0.005),
        # 5000                1/1250  --> 3/2500  +50%
        ("mythic", 0.0008),
    ],
    1: [
        ("common", 0.6481),
        ("uncommon", 0.27),
        ("rare", 0.06),
        ("epic", 0.015),
        ("legendary", 0.006),
        ("mythic", 0.0009),
    ],
    2: [
        ("common", 0.612),
        ("uncommon", 0.29),
        ("rare", 0.07),
        ("epic", 0.02),
        ("legendary", 0.007),
        ("mythic", 0.00010),
    ],
    3: [
        ("common", 0.5759),
        ("uncommon", 0.31),
        ("rare", 0.08),
        ("epic", 0.025),
        ("legendary", 0.008),
        ("mythic", 0.0011),
    ],
    4: [
        ("common", 0.5398),
        ("uncommon", 0.33),
        ("rare", 0.09),
        ("epic", 0.03),
        ("legendary", 0.009),
        ("mythic", 0.0012),
    ],
    5: [
        ("common", 0.5038),
        ("uncommon", 0.35),
        ("rare", 0.1),
        ("epic", 0.035),
        ("legendary", 0.01),
        ("mythic", 0.0012),
    ],
}

# Line upgrade that increases the chance of catching two fish in one cast
LINE_UPGRADES = {
    0: 10000,
    1: 7500,
    2: 5000,
    3: 2500,
    4: 500,
    5: 100,
}

# Lure upgrades to give users a better chance at special fish
LURE_UPGRADES = {
    0: 0.0100,
    1: 0.0150,
    2: 0.0225,
    3: 0.0338,
    4: 0.0506,
    5: 0.0759,
}

# Crate chance upgrade that increases the chance of catching a crate
CRATE_CHANCE_UPGRADE = {0: 252, 1: 216, 2: 180, 3: 144, 4: 108, 5: 72}

# Weight upgrade that increases the level of the caught fish
WEIGHT_UPGRADES = {
    0: (1, 2),
    1: (5, 10),
    2: (10, 15),
    3: (10, 25),
    4: (10, 50),
    5: (25, 50),
}

# Crate tier upgrade that increases the tier of the crate and the items inside
CRATE_TIER_UPGRADE = {
    0: (1.0, 0, 0, 0, 0, 0),
    1: (0.89, 0.1, 0.01, 0, 0, 0),
    2: (0.74, 0.2, 0.05, 0.01, 0, 0),
    3: (0.54, 0.3, 0.1, 0.05, 0.01, 0),
    4: (0.29, 0.4, 0.15, 0.1, 0.05, 0.01),
    5: (0, 0.5, 0.2, 0.15, 0.1, 0.05),
}

# Tiers for the crates and what is inside them
# (sand dollars, casts, chances of fish bags, amount of fish bags,
# changes of food, amount of food, chances of potions, amount of potions)
CRATE_TIERS = {
    "Wooden": (
        500,
        1,
        (1.0, 0, 0, 0, 0, 0),
        1,
        (1.0, 0, 0, 0),
        1,
        (1.0, 0, 0, 0),
        1,
    ),
    "Bronze": (
        1000,
        2,
        (0.89, 0.1, 0.01, 0, 0, 0),
        2,
        (0.89, 0.1, 0.01, 0),
        2,
        (0.89, 0.1, 0.01, 0),
        1,
    ),
    "Steel": (
        2500,
        5,
        (0.74, 0.2, 0.05, 0.01, 0, 0),
        4,
        (0.74, 0.2, 0.05, 0.01),
        4,
        (0.74, 0.2, 0.05, 0.01),
        1,
    ),
    "Golden": (
        5000,
        10,
        (0.54, 0.3, 0.1, 0.05, 0.01, 0),
        7,
        (0.54, 0.3, 0.1, 0.05),
        7,
        (0.54, 0.3, 0.1, 0.05),
        2,
    ),
    "Diamond": (
        10000,
        20,
        (0.29, 0.4, 0.15, 0.1, 0.05, 0.01),
        11,
        (0.29, 0.4, 0.15, 0.1),
        11,
        (0.29, 0.4, 0.15, 0.1),
        2,
    ),
    "Enchanted": (
        50000,
        100,
        (0, 0.5, 0.2, 0.15, 0.1, 0.05),
        16,
        (0, 0.5, 0.2, 0.15),
        16,
        (0, 0.5, 0.2, 0.15),
        3,
    ),
}


BLEACH_UPGRADE = {0: 1, 1: 1.3, 2: 1.6, 3: 1.9, 4: 2.2, 5: 2.5}

# Toys upgrade that increases the amount of xp gained
TOYS_UPGRADE = {
    0: (10, 30),
    1: (25, 75),
    2: (50, 150),
    3: (100, 300),
    4: (150, 450),
    5: (200, 600),
}

# Amazement upgrade increases the chance of a fish to gain a level
# when entertained
AMAZEMENT_UPGRADE = {0: 1600, 1: 1500, 2: 1300, 3: 1000, 4: 600, 5: 100}

# Mutation upgrade increases the chance of a fish to mutate to
# golden or inverted after being in a tank cleaned
MUTATION_UPGRADE = {0: 5000, 1: 4000, 2: 3000, 3: 2000, 4: 1000, 5: 500}

# Big servings upgrade increases the chance of fish food not being
# consumed when a fish is fed
BIG_SERVINGS_UPGRADE = {0: 500, 1: 350, 2: 250, 3: 100, 4: 50, 5: 10}

# Hygienic upgrade increases the time between cleans
# and the multiplier with that time
HYGIENIC_UPGRADE = {
    0: (1, 60),
    1: (4, 240),
    2: (8, 480),
    3: (12, 720),
    4: (16, 960),
    5: (24, 1440),
}

# Feeding upgrade increases the time before a fish dies from not being fed
FEEDING_UPGRADES = {
    0: (1, 0),
    1: (1, 12),
    2: (2, 0),
    3: (2, 12),
    4: (3, 0),
    5: (3, 12),
}


def special_percentage_finder(upgrade_level):
    """
    Returns the results of the lure upgrade
    [(list of types), (list of chances)]
    """
    return [
        list(i[0] for i in LURE_UPGRADES[upgrade_level]),
        list(i[1] for i in LURE_UPGRADES[upgrade_level]),
    ]


def rarity_percentage_finder(
    upgrade_level: int,
) -> Tuple[List[str], List[float]]:
    """
    Returns the results of the bait upgrade
    [(list of rarities), (list of chances)]
    """
    return [
        list(i[0] for i in BAIT_UPGRADE[upgrade_level]),
        list(i[1] for i in BAIT_UPGRADE[upgrade_level]),
    ]
