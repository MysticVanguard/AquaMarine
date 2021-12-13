from os import walk
import asyncio

import discord


"""
The following utils are for upgrades used in various commands
throughout the bot, and are based on the level of the upgrade
"""


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
    0: [("normal", 0.1000), ("inverted", 0.0000), ("golden", 0.0000)],
    1: [("normal", 0.9989), ("inverted", 0.0010), ("golden", 0.0001)],
    2: [("normal", 0.9978), ("inverted", 0.0020), ("golden", 0.0002)],
    3: [("normal", 0.9967), ("inverted", 0.0030), ("golden", 0.0003)],
    4: [("normal", 0.9956), ("inverted", 0.0040), ("golden", 0.0004)],
    5: [("normal", 0.9945), ("inverted", 0.0050), ("golden", 0.0005)],
}

# Crate chance upgrade that increases the chance of catching a crate
CRATE_CHANCE_UPGRADE = {0: 2190, 1: 1570, 2: 1080, 3: 540, 4: 360, 5: 180}

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


BLEACH_UPGRADE = {0: 1, 1: 1.4, 2: 1.8, 3: 2.2, 4: 2.6, 5: 3.0}

# Toys upgrade that increases the amount of xp gained
TOYS_UPGRADE = {
    0: (5, 50),
    1: (15, 75),
    2: (25, 125),
    3: (50, 250),
    4: (100, 500),
    5: (200, 1000),
}

# Amazement upgrade increases the chance of a fish to gain a level
# when entertained
AMAZEMENT_UPGRADE = {0: 1600, 1: 1500, 2: 1300, 3: 1000, 4: 600, 5: 100}

# Mutation upgrade increases the chance of a fish to mutate to
# golden or inverted after being *****TBD
MUTATION_UPGRADE = {0: 50000, 1: 40000, 2: 30000, 3: 20000, 4: 10000, 5: 5000}

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
    0: (3, 0),
    1: (3, 6),
    2: (3, 12),
    3: (3, 18),
    4: (3, 24),
    5: (4, 6),
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
) -> tuple[list[str], list[float]]:
    """
    Returns the results of the bait upgrade
    [(list of rarities), (list of chances)]
    """
    return [
        list(i[0] for i in BAIT_UPGRADE[upgrade_level]),
        list(i[1] for i in BAIT_UPGRADE[upgrade_level]),
    ]  # type:ignore


"""
The following utils are used for commands that use emojis
such as slots and gamble
"""

"""
Other utils with various uses
"""

# The different acceptable names for items bought in the shop
COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
INVERTED_BAG_NAMES = ["Inverted Fish Bag", "Inverted", "Ifb"]
HIGH_LEVEL_BAG_NAMES = ["High Level Fish Bag", "High Level", "Hlfb"]
FISH_FLAKES_NAMES = ["Fish Flakes", "Flakes", "Ff"]
FISH_BOWL_NAMES = ["Fish Bowl", "Bowl", "Fb"]
SMALL_TANK_NAMES = ["Small Tank", "Small", "St"]
MEDIUM_TANK_NAMES = ["Medium Tank", "Medium", "Mt"]
PLANT_LIFE_NAMES = ["Plant Life", "Plant", "Pl"]
FISH_REVIVAL_NAMES = ["Fish Revival", "Revival", "Fr"]
CASTS_NAMES = ["Fishing Casts", "Casts", "Fc"]
SAND_DOLLAR_NAMES = ["Sand Dollars", "Dollars", "Sd"]
FISH_PELLETS_NAMES = ["Fish Pellets", "Pellets", "Fp"]
FISH_WAFERS_NAMES = ["Fish Wafers", "Wafers", "Fw"]
FISH_POINTS_NAMES = ["Fish Points", "Points", "P"]
EXPERIENCE_POTION_NAMES = ["Experience Potion", "Experience", "E"]
MUTATION_POTION_NAMES = ["Mutation Potion", "Mutation", "M"]
FEEDING_POTION_NAMES = ["Feeding Potion", "Feeding", "F"]

# List of names for tank themes
TANK_THEMES = PLANT_LIFE_NAMES

# Daylight savings variable because for some reason i need to
# add four and then an hour when its daylight savings,
# will be changed to 4 when daylight savings is over
DAYLIGHT_SAVINGS = 5

# What colors the embed should have based on rarity
RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090,  # Hot Pink
}

# This parses file names


def parse_fish_filename(filename: str) -> dict:
    """
    Parse a given fish filename into a dict of `modifier`, `rarity`, `cost`,
    `raw_name`, and `name`.
    """

    # Initial filename splitterboi
    filename = filename[:-4]  # Remove file extension
    modifier = None
    # Splits the formatted file name into its parts
    rarity, cost, size, *raw_name = filename.split("_")

    # See if our fish name has a modifier on it
    # If rarity is actually the modifier...
    if rarity in ["inverted", "golden"]:
        # Change the variables to what they actually should be
        modifier, rarity, cost, size, raw_name = (
            rarity,
            cost,
            size,
            raw_name[0],
            raw_name[1:],
        )
    # Make sure the raw name is the name with underscores joining
    raw_name = "_".join(raw_name)

    # Return the parts of the filename in a dict of the stats
    return {
        "modifier": modifier,
        "rarity": rarity,
        "cost": cost,
        "size": size,
        "raw_name": raw_name,
        # make the name "Example Text" instead of "example_text"
        "name": raw_name.replace("_", " ").title(),
    }


def fetch_fish(directory: str) -> dict:
    """
    Fetch all of the fish from a given directory.
    """

    # Set up a dict of fish the we want to append/return to
    fetched_fish = {
        "common": {},
        "uncommon": {},
        "rare": {},
        "epic": {},
        "legendary": {},
        "mythic": {},
    }

    # Grab all the filenames from the given directory
    _, _, fish_filenames = next(walk(directory))

    # Go through each filename
    for filename in fish_filenames:

        # Add the fish to the dict
        fish_data = parse_fish_filename(filename)
        if fish_data["modifier"]:
            continue  # We don't care about inverted/golden fish here
        fetched_fish[fish_data["rarity"]][fish_data["name"].lower()] = {
            "image": f"{directory}/{filename}",
            **fish_data,
        }

    return fetched_fish


def make_golden(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it golden.
    """

    # Adds the modifier to the raw name
    fish["raw_name"] = f"golden_{fish['raw_name']}"
    # Adds the modifier to the name
    fish["name"] = f"Golden {fish['name']}"
    # Adds the modifier to the image folder path in the correct place
    fish["image"] = fish["image"][:40] + "golden_" + fish["image"][40:]
    return fish


def make_inverted(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it inverted.
    """

    # Adds the modifier to the raw name
    fish["raw_name"] = f"inverted_{fish['raw_name']}"
    fish["name"] = f"Inverted {fish['name']}"  # Adds the modifier to the name
    # Adds the modifier to the image folder path in the correct place
    fish["image"] = fish["image"][:40] + "inverted_" + fish["image"][40:]
    return fish


def get_normal_name(fish_name):
    """Get the unmodified fish name by removing inverted/golden prefix"""

    fish_name = fish_name.strip("inverted_")
    fish_name = fish_name.strip("golden_")
    return fish_name


async def create_select_menu(bot, ctx, option_list, type_noun, type_verb):
    """
    This will create a select menu from the given list,
    have the user select one, and return the selection
    """

    # Initiates the option list
    test_options = []

    # For each name that isnt "" add it as an option for the select menu
    for option in option_list:
        if option != "":
            test_options.append(
                discord.ui.SelectOption(label=option, value=option)
            )

    # Set the select menu with the options
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.SelectMenu(
                custom_id=type_verb,
                options=test_options,
                placeholder="Select an option",
            )
        )
    )

    # Ask them what they want to do with component
    message = await ctx.send(
        f"What {type_noun} would you like to {type_verb}?",
        components=components,
    )

    # If it's the correct message and author return true
    def check(payload):
        if payload.message.id != message.id:
            return False

        # If its the wrong author send an ephemeral message
        if payload.user.id != ctx.author.id:
            bot.loop.create_task(
                payload.response.send_message(
                    "You can't respond to this message!", ephemeral=True
                )
            )
            return False
        return True

    # If it works don't fail, and if it times out say that
    try:
        payload = await bot.wait_for(
            "component_interaction", check=check, timeout=60
        )
        await payload.response.defer_update()
    except asyncio.TimeoutError:
        return await ctx.send(
            f"Timed out asking for {type_noun} to "
            f"{type_verb} <@{ctx.author.id}>"
        )

    # Return what they chose
    return str(payload.values[0])


# This is a list of fish that are no longer able to be caught
past_fish = ["acorn_goldfish", "cornucopish", "turkeyfish"]
