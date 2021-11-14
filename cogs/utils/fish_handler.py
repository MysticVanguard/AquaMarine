from os import walk
import re
import typing

'''
The following utils are for upgrades used in various commands throughout the bot, and are based on the level of the upgrade
'''
# Lure upgrades to give users a better chance at special fish
LURE_UPGRADES = {
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

# Bait upgrade that increases your chances of catching rarer fish
BAIT_UPGRADE = {
    1: [
        ("common", 0.6689),
        ("uncommon", 0.2230),
        ("rare", 0.0743),
        ("epic", 0.0248),
        ("legendary", 0.0082),
        ("mythic", 0.0008),
    ],
    2: [
        ("common", 0.6689),
        ("uncommon", 0.2230),
        ("rare", 0.0743),
        ("epic", 0.0248),
        ("legendary", 0.0082),
        ("mythic", 0.0008),
    ],
    3: [
        ("common", 0.6429),
        ("uncommon", 0.2330),
        ("rare", 0.0843),
        ("epic", 0.0298),
        ("legendary", 0.0092),
        ("mythic", 0.0008),
    ],
    4: [
        ("common", 0.6168),
        ("uncommon", 0.2430),
        ("rare", 0.0943),
        ("epic", 0.0348),
        ("legendary", 0.0102),
        ("mythic", 0.0009),
    ],
    5: [
        ("common", 0.5908),
        ("uncommon", 0.2530),
        ("rare", 0.1043),
        ("epic", 0.0398),
        ("legendary", 0.0112),
        ("mythic", 0.0009),
    ],
    6: [
        ("common", 0.5697),
        ("uncommon", 0.2630),
        ("rare", 0.1143),
        ("epic", 0.0448),
        ("legendary", 0.0122),
        ("mythic", 0.0010),
    ],
    7: [
        ("common", 0.5387),
        ("uncommon", 0.2730),
        ("rare", 0.1243),
        ("epic", 0.0498),
        ("legendary", 0.0132),
        ("mythic", 0.0010),
    ],
    8: [
        ("common", 0.5126),
        ("uncommon", 0.2830),
        ("rare", 0.1343),
        ("epic", 0.0548),
        ("legendary", 0.0142),
        ("mythic", 0.0011),
    ],
    9: [
        ("common", 0.4866),
        ("uncommon", 0.2930),
        ("rare", 0.1443),
        ("epic", 0.0598),
        ("legendary", 0.0152),
        ("mythic", 0.0011),
    ],
    10: [
        ("common", 0.4605),
        ("uncommon", 0.3030),
        ("rare", 0.1543),
        ("epic", 0.0648),
        ("legendary", 0.0162),
        ("mythic", 0.0012),
    ],
}

# Weight upgrade that increases the level of the caught fish
WEIGHT_UPGRADES = {1: (1, 2), 2: (3, 10), 3: (5, 15), 4: (8, 20), 5: (10, 25)}

# Rod upgrade that increases the multiplier of a fish when it is sold
ROD_UPGRADES = {1: 1, 2: 1.1, 3: 1.1, 4: 1.2, 5: 1.3}

# Line upgrade that increases the chance of catching two fish in one cast
LINE_UPGRADES = {
    1: 10000,
    2: 10000,
    3: 9950,
    4: 9900,
    5: 9800,
    6: 9700,
    7: 8700,
    8: 7000,
    9: 5500,
    10: 3500,
}

# Feeding upgrade that increases the time before a fish dies from not being fed
FEEDING_UPGRADES = {1: (3, 0), 2: (3, 3), 3: (3, 6), 4: (3, 9), 5: (3, 12)}

# Toys upgrade that increases the amount of xp gained
TOYS_UPGRADE = {1: (2, 40), 2: (2, 40), 3: (4, 50), 4: (6, 60), 5: (10, 80), 6: (15, 100), 7: (20, 120), 8: (30, 150), 9: (45, 180), 10: (65, 225)}

# Amazement upgrade increases the chance of a fish to gain a level when entertained
AMAZEMENT_UPGRADE = {1: 1000, 2: 900, 3: 800, 4: 700, 5: 600}

# Bleach upgrade increases the multiplier of sand dollars gained from cleaning
BLEACH_UPGRADE = {1: 1, 2: 1, 3: 1.1, 4: 1.2, 5: 1.3, 6: 1.5, 7: 1.7, 8: 2.0, 9: 2.5, 10: 3.0}

# Hygienic upgrade increases the time between cleans and the multiplier with that time
HYGIENIC_UPGRADE = {1: (1, 60), 2: (3, 180), 3: (6, 360), 4: (12, 720), 5: (24, 1240)}

# This returns the results of the lure upgrade in [(list of types), (list of chances)]
def special_percentage_finder(upgrade_level):
    return [
        list(i[0] for i in LURE_UPGRADES[upgrade_level]),
        list(i[1] for i in LURE_UPGRADES[upgrade_level]),
    ]

# This returns the results of the bait upgrade in [(list of rarities), (list of chances)]
def rarity_percentage_finder(upgrade_level: int) -> typing.List[float]:
    return [
        list(i[0] for i in BAIT_UPGRADE[upgrade_level]),
        list(i[1] for i in BAIT_UPGRADE[upgrade_level]),
    ]


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
CASTS_NAMES = ["Fishing Casts", "Casts", "C"]

# Daylight savings variable because for some reason i need to add four and then an hour when its daylight savings, will be changed to 4 when daylight savings is over
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
    rarity, cost, size, *raw_name = filename.split("_") # Splits the formatted file name into its parts

    # See if our fish name has a modifier on it
    if rarity in ["inverted", "golden"]: # If rarity is actually the modifier...
        modifier, rarity, cost, size, raw_name = rarity, cost, size, raw_name[0], raw_name[1:] # Change the variables to what they actually should be
    raw_name = "_".join(raw_name) # Make sure the raw name is the name with underscores joining

    # Return the parts of the filename in a dict of the stats
    return {
        "modifier": modifier,
        "rarity": rarity,
        "cost": cost,
        "size": size,
        "raw_name": raw_name,
        "name": raw_name.replace("_", " ").title(), # make the name "Example Text" instead of "example_text"
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

    fish["raw_name"] = f"golden_{fish['raw_name']}" # Adds the modifier to the raw name
    fish["name"] = f"Golden {fish['name']}" # Adds the modifier to the name
    fish["image"] = fish["image"][:40] + "golden_" + fish["image"][40:] # Adds the modifier to the image folder path in the correct place
    return fish

# This will make the fish inverted
def make_inverted(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it inverted.
    """

    fish["raw_name"] = f"inverted_{fish['raw_name']}" # Adds the modifier to the raw name
    fish["name"] = f"Inverted {fish['name']}" # Adds the modifier to the name
    fish["image"] = fish["image"][:40] + "inverted_" + fish["image"][40:] # Adds the modifier to the image folder path in the correct place
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
