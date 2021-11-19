from os import walk
import re
import typing

import asyncio
import discord
from discord.ext import vbu

'''
The following utils are for upgrades used in various commands throughout the bot, and are based on the level of the upgrade
'''


# Rod upgrade that increases the multiplier of a fish when it is sold
ROD_UPGRADES = {0: 1, 1: 1.1, 2: 1.3, 3: 1.6, 4: 2.0, 5: 2.5}

# Bait upgrade that increases your chances of catching rarer fish
BAIT_UPGRADE = {
    0: [
        ("common", 0.6689),
        ("uncommon", 0.2230),
        ("rare", 0.0743),
        ("epic", 0.0248),
        ("legendary", 0.0082),
        ("mythic", 0.0008),
    ],
    1: [
        ("common", 0.6429),
        ("uncommon", 0.2330),
        ("rare", 0.0843),
        ("epic", 0.0298),
        ("legendary", 0.0092),
        ("mythic", 0.0008),
    ],
    2: [
        ("common", 0.5908),
        ("uncommon", 0.2530),
        ("rare", 0.1043),
        ("epic", 0.0398),
        ("legendary", 0.0112),
        ("mythic", 0.0009),
    ],
    3: [
        ("common", 0.5387),
        ("uncommon", 0.2730),
        ("rare", 0.1243),
        ("epic", 0.0498),
        ("legendary", 0.0132),
        ("mythic", 0.0010),
    ],
    4: [
        ("common", 0.4866),
        ("uncommon", 0.2930),
        ("rare", 0.1443),
        ("epic", 0.0598),
        ("legendary", 0.0152),
        ("mythic", 0.0011),
    ],
    5: [
        ("common", 0.4605),
        ("uncommon", 0.3030),
        ("rare", 0.1543),
        ("epic", 0.0648),
        ("legendary", 0.0162),
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
    0: [
        ("normal", .1000),
        ("inverted", .0000),
        ("golden", .0000)
    ],
    1: [
        ("normal", .9989),
        ("inverted", .0010),
        ("golden", .0001)
    ],
    2: [
        ("normal", .9978),
        ("inverted", .0020),
        ("golden", .0002)
    ],
    3: [
        ("normal", .9967),
        ("inverted", .0030),
        ("golden", .0003)
    ],
    4: [
        ("normal", .9956),
        ("inverted", .0040),
        ("golden", .0004)
    ],
    5: [
        ("normal", .9945),
        ("inverted", .0050),
        ("golden", .0005)
    ]
}

# Crate chance upgrade that increases the chance of catching a crate
CRATE_CHANCE_UPGRADE = {0: 2190, 1: 1570, 2: 1080, 3: 540, 4: 360, 5: 180}

# Weight upgrade that increases the level of the caught fish
WEIGHT_UPGRADES = {0: (1, 2), 1: (5, 10), 2: (
    10, 15), 3: (10, 25), 4: (10, 50), 5: (25, 50)}

# Crate tier upgrade that increases the tier of the crate and the items inside
CRATE_TIER_UPGRADE = {
    0: (1.0, 0, 0, 0, 0, 0),
    1: (.89, .1, .01, 0, 0, 0),
    2: (.74, .2, .05, .01, 0, 0),
    3: (.54, .3, .1, .05, .01, 0),
    4: (.29, .4, .15, .1, .05, .01),
    5: (0, .5, .2, .15, .1, 0.05)
}

# Tiers for the crates and what is inside them (sand dollars, casts, chances of fish bags, amount of fish bags, changes of food, amount of food, chances of potions, amount of potions)
CRATE_TIERS = {
    "Wooden": (500, 1, (1.0, 0, 0, 0, 0, 0), 1, (1.0, 0, 0, 0), 1, (1.0, 0, 0, 0), 1),
    "Bronze": (1000, 2, (.89, .1, .01, 0, 0, 0), 2, (.89, .1, .01, 0), 2, (.89, .1, .01, 0), 1),
    "Steel": (2500, 5, (.74, .2, .05, .01, 0, 0), 4, (.74, .2, .05, .01), 4, (.74, .2, .05, .01), 1),
    "Golden": (5000, 10, (.54, .3, .1, .05, .01, 0), 7, (.54, .3, .1, .05), 7, (.54, .3, .1, .05), 2),
    "Diamond": (10000, 20, (.29, .4, .15, .1, .05, .01), 11, (.29, .4, .15, .1), 11, (.29, .4, .15, .1), 2),
    "Enchanted": (50000, 100, (0, .5, .2, .15, .1, 0.05), 16, (0, .5, .2, .15), 16, (0, .5, .2, .15), 3),
}


# Bleach upgrade increases the multiplier of sand dollars gained from cleaning
BLEACH_UPGRADE = {0: 1, 1: 1.1, 2: 1.3, 3: 1.6, 4: 2.0, 5: 2.5}

# Toys upgrade that increases the amount of xp gained
TOYS_UPGRADE = {0: (2, 40), 1: (5, 50), 2: (10, 100),
                3: (25, 125), 4: (35, 150), 5: (50, 250)}

# Amazement upgrade that increases the chance of a fish to gain a level when entertained
AMAZEMENT_UPGRADE = {0: 1600, 1: 1500, 2: 1300, 3: 1000, 4: 600, 5: 100}

# Mutation upgrade that increases the chance of a fish to mutate to golden or inverted after being *****TBD
MUTATION_UPGRADE = {0: 50000, 1: 40000, 2: 30000, 3: 20000, 4: 10000, 5: 5000}

# Big servings upgrade that increases the chance of fish food not being consumed when a fish is fed
BIG_SERVINGS_UPGRADE = {0: 500, 1: 350, 2: 250, 3: 100, 4: 50, 5: 10}

# Hygienic upgrade increases the time between cleans and the multiplier with that time
HYGIENIC_UPGRADE = {0: (1, 60), 1: (4, 240), 2: (
    8, 480), 3: (12, 720), 4: (16, 960), 5: (24, 1440)}

# Feeding upgrade that increases the time before a fish dies from not being fed
FEEDING_UPGRADES = {0: (3, 0), 1: (3, 6), 2: (
    3, 12), 3: (3, 18), 4: (3, 24), 5: (4, 6)}


# This returns the results of the lure upgrade in [(list of types), (list of chances)]
def special_percentage_finder(upgrade_level):
    return [
        list(i[0] for i in LURE_UPGRADES[upgrade_level]),
        list(i[1] for i in LURE_UPGRADES[upgrade_level]),
    ]

# This returns the results of the bait upgrade in [(list of rarities), (list of chances)]


def rarity_percentage_finder(upgrade_level: int) -> typing.Tuple[typing.List[str], typing.List[float]]:
    return [
        list(i[0] for i in BAIT_UPGRADE[upgrade_level]),
        list(i[1] for i in BAIT_UPGRADE[upgrade_level]),
    ]  # type:ignore


'''
The following utils are used for commands that use emojis such as slots and gamble
'''

# A dictionary of every fish and its emoji_id counterpart, seperated by rarity
EMOJI_RARITIES = {
    "common": {
        "clownfish": "<:clownfish:878370648936820786>",
        "goldfish": "<:goldfish:878370648618074114>",
        "tiger_barb": "<:tiger_barb:878370648890679328>",
        "royal_blue_betta": "<:royal_blue_betta:878370648722915350>",
        "pufferfish": "<:pufferfish:878370650199314542>",
        "oscar_cichlid": "<:oscar_cichlid:878370649972834324>",
        "neon_tetra_school": "<:neon_tetra_school:878370648949395496>",
        "turquoise_blue_betta": "<:turquoise_blue_betta:878370649146556466>",
        "tuna": "<:tuna:878379351995998299>",
        "squid": "<:squid:878370649620484127>",
        "shrimp": "<:shrimp:878370648890679308>",
        "red_betta": "<:red_betta:878370648748097536>",
        "paradise_fish": "<:paradise_fish:878370648999743508>",
        "koi": "<:koi:878370649482100766>",
        "headshield_slug": "<:headshield_slug:878370648701931521>",
        "guppies": "<:guppies:878370648974561310>",
        "electric_blue_hap": "<:electric_blue_hap:878370648924246096>",
        "cowfish": "<:cowfish:878370649184301087>",
        "clown_triggerfish": "<:clown_triggerfish:878379011133280256>",
        "angelfish": "<:angelfish:878370649503039488>",
        "pineapple_betta": "<:pineapple_betta:878370648987152434>",
        "harlequin_rasboras": "<:harlequin_rasboros:878370648899063878>",
        "electric_yellow_lab": "<:electric_yellow_lab:878370648928448562>",
        "catfish": "<:catfish:878378925888245760>",
        "blue_maomao": "<:blue_maomao:878370649524039700>",
        "blue_diamond_discus": "<:blue_diamond_discus:878370648945229834>",
        "black_orchid_betta": "<:black_orchid_betta:878370649431740477>",
        "banggai_cardinalfish": "<:banggai_cardinalfish:878370648894869605>",
        "bottlenose_dolphin": "<:bottlenose_dolphin:878370649075240991>",
        "starfish": "<:starfish:878377160870592522>",
        "bluefin_notho": "<:bluefin_notho:878370648529969173>",
        "giant_sea_bass": "<:giant_sea_bass:878370648970387506>",
        "gold_doubloon_molly": "<:gold_doubloon_molly:878370648932626542>",
        "raccoon_butterflyfish": "<:raccoon_butterflyfish:878370649456922694>",
        "rainbow_kribensis_cichlid": "<:rainbow_kribensis_cichlid:878370648932638790>",
        "regal_blue_tang": "<:regal_blue_tang:878370650039918692>",
        "sea_goldie": "<:sea_goldie:878370649180106752>",
        "yellow_tang": "<:yellow_tang:878370649897328650>",
        "zebra_danios": "<:zebra_danios:878370648852922429>",
        "carp": "<:carp:878377327271227462>"
    },
    "uncommon": {
        "flowerhorn_cichlid": "<:flowerhorn_cichlid:878380626644979762>",
        "lionfish": "<:lionfish:878380626863091732>",
        "sea_bunny": "<:sea_bunny:878370649385603172>",
        "manta_ray": "<:manta_ray:878380627613864037>",
        "surge_wrasse": "<:surge_wrasse:878380626561081414>",
        "smalltooth_swordfish": "<:smalltooth_swordfish:878380626615631953>",
        "seal": "<:seal:878370649289142304>",
        "seahorse": "<:seahorse:878370649888919573>",
        "quoyi_parrotfish": "<:quoyi_parrotfish:878370650241249290>",
        "narwhal": "<:narwhal:878370649935073410>",
        "dumbo_octopus": "<:dumbo_octopus:878370650060902460>",
        "red_handfish": "<:red_handfish:878370649448534026>",
        "walking_batfish": "<:walking_batfish:878370649867960330>",
        "black_drakefish": "<:black_drakefish:878380261363056710>",
        "blue_drakefish": "<:blue_drakefish:878380261153329272>",
        "green_drakefish": "<:green_drakefish:878380261203644436>",
        "manatee": "<:manatee:878380626477211688>",
        "red_drakefish": "<:red_drakefish:878380261363036160>",
        "victory_drakefish": "<:victory_drakefish:878380261379825724>",
        "orca": "<:orca:878379352499310712>",
        "whale_shark": "<:whale_shark:878379353015197817>",
        "mandarinfish": "<:mandarinfish:878379851776679986>"
    },
    "rare": {
        "axolotl": "<:axolotl:878370649893109790>",
        "blobfish": "<:blobfish:878370649943441418>",
        "cuttlefish": "<:cuttlefish:878370649893109780>",
        "starfish_with_pants": "<:starfish_with_pants:878380007947386932>",
        "bobtail_squid": "<:bobtail_squid:878370649880543252>",
        "mantis_shrimp": "<:mantis_shrimp:878370649872146512>",
        "school_of_betta": "<:school_of_betta:878380008287133827>",
        "atlantic_sturgeon": "<:atlantic_sturgeon:878370649511432232>"
    },
    "epic": {
        "asian_arowana": "<:asian_arowana:878379497731276861>",
        "boesemani_rainbowfish": "<:boesemani_rainbowfish:878370649465311232>"
    },
    "legendary": {
        "anglerfish": "<:anglerfish:878379836064825354>"
    },
    "mythic": {
    }
}

# These are the fish and fish ids that are a part of the gamble command
EMOJI_RARITIES_SET_ONE = {
    "common": {
        "clownfish": "<:clownfish:878370648936820786>",
        "goldfish": "<:goldfish:878370648618074114>",
        "tiger_barb": "<:tiger_barb:878370648890679328>",
        "royal_blue_betta": "<:royal_blue_betta:878370648722915350>",
        "pufferfish": "<:pufferfish:878370650199314542>",
        "oscar_cichlid": "<:oscar_cichlid:878370649972834324>",
        "neon_tetra_school": "<:neon_tetra_school:878370648949395496>"
    },
    "uncommon": {
        "flowerhorn_cichlid": "<:flowerhorn_cichlid:878380626644979762>",
        "lionfish": "<:lionfish:878380626863091732>"
    },
    "legendary": {
        "anglerfish": "<:anglerfish:878379836064825354>"
    },
}


'''
Other utils with various uses
'''

# The different acceptable names for items bought in the shop
COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
FISH_FLAKES_NAMES = ["Fish Flakes", "Flakes", "Ff"]
FISH_BOWL_NAMES = ["Fish Bowl", "Bowl", "Fb"]
SMALL_TANK_NAMES = ["Small Tank", "Small", "St"]
MEDIUM_TANK_NAMES = ["Medium Tank", "Medium", "Mt"]
PLANT_LIFE_NAMES = ["Plant Life", "Plant", "Pl"]
FISH_REVIVAL_NAMES = ["Fish Revival", "Revival", "Fr"]
CASTS_NAMES = ["Fishing Casts", "Casts", "Fc"]
SAND_DOLLAR_NAMES = ["Sand Dollars", "Dollars", "Sd"]

# Daylight savings variable because for some reason i need to add four and then an hour when its daylight savings,
# will be changed to 4 when daylight savings is over
DAYLIGHT_SAVINGS = 5

# What colors the embed should have based on rarity
RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090  # Hot Pink
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
        modifier, rarity, cost, size, raw_name = rarity, cost, size, raw_name[0], raw_name[1:]
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
        if fish_data['modifier']:
            continue  # We don't care about inverted/golden fish here
        fetched_fish[fish_data['rarity']][fish_data['name'].lower()] = {
            "image": f"{directory}/{filename}",
            **fish_data,
        }

    return fetched_fish

# This will make the fish golden


def make_golden(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it golden.
    """

    # Adds the modifier to the raw name
    fish["raw_name"] = f"golden_{fish['raw_name']}"
    fish["name"] = f"Golden {fish['name']}"  # Adds the modifier to the name
    # Adds the modifier to the image folder path in the correct place
    fish["image"] = fish["image"][:40] + "golden_" + fish["image"][40:]
    return fish

# This will make the fish inverted


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

# This will get rid of any modifiers


def get_normal_name(fish_name):
    """
    Get the non-inverted/golden name for the fish
    """

    # If there is inverted or golden at the front of the fish name, take it off
    match = re.match(r"(inverted_|golden_)(?P<fish_name>.*)", fish_name)
    if match:
        return match.group("fish_name")
    return fish_name


# This will create a select menu from the given list, have the user select one, and return the selection
async def create_select_menu(bot, ctx, option_list, type_noun, type_verb):

    # Initiates the option list
    test_options = []

    # For each name that isnt "" add it as an option for the select menu
    for option in option_list:
        if option != "":
            test_options.append(discord.ui.SelectOption(
                label=option, value=option))

    # Set the select menu with the options
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.SelectMenu(custom_id=type_verb,
                                  options=test_options,
                                  placeholder="Select an option",
                                  )
        )
    )

    # Ask them what they want to do with component
    message = await ctx.send(f"What {type_noun} would you like to {type_verb}?", components=components)

    # If it's the correct message and author return true
    def check(payload):
        if payload.message.id != message.id:
            return False

        # If its the wrong author send an ephemeral message
        if payload.user.id != ctx.author.id:
            bot.loop.create_task(payload.response.send_message(
                "You can't respond to this message!", ephemeral=True))
            return False
        return True

    # If it works don't fail, and if it times out say that
    try:
        payload = await bot.wait_for("component_interaction", check=check, timeout=60)
        await payload.response.defer_update()
    except asyncio.TimeoutError:
        return await ctx.send(f"Timed out asking for {type_noun} to {type_verb} <@{ctx.author.id}>")

    # Return what they chose
    return str(payload.values[0])
