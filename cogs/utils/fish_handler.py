from os import walk
import re
import typing


SPECIAL_RARITY_PERCENTAGES = {
    1: [
        ("normal", .94),
        ("inverted", .05),
        ("golden", .01)
    ],
    2: [
        ("normal", .90),
        ("inverted", .08),
        ("golden", .02)
    ],
    3: [
        ("normal", .85),
        ("inverted", .12),
        ("golden", .03)
    ],
    4: [
        ("normal", .78),
        ("inverted", .18),
        ("golden", .04)
    ],
    5: [
        ("normal", .67),
        ("inverted", .27),
        ("golden", .06)
    ]
}

_RARITY_PERCENTAGES = {
    1: [
        ("common", 0.6689),
        ("uncommon", 0.2230),
        ("rare", 0.0743),
        ("epic", 0.0248),
        ("legendary", 0.0082),
        ("mythic", 0.0008),
    ],
    2: [
        ("common", 0.6062),
        ("uncommon", 0.2423),
        ("rare", 0.0967),
        ("epic", 0.0385),
        ("legendary", 0.0154),
        ("mythic", 0.0009),
    ],
    3: [
        ("common", 0.5156),
        ("uncommon", 0.2578),
        ("rare", 0.1289),
        ("epic", 0.0645),
        ("legendary", 0.0322),
        ("mythic", 0.0010),
    ],
    4: [
        ("common", 0.4558),
        ("uncommon", 0.2605),
        ("rare", 0.1490),
        ("epic", 0.0850),
        ("legendary", 0.0486),
        ("mythic", 0.0011),
    ],
    5: [
        ("common", 0.3843),
        ("uncommon", 0.2558),
        ("rare", 0.1701),
        ("epic", 0.1134),
        ("legendary", 0.0752),
        ("mythic", 0.0012),
    ]
}

RARITY_PERCENTAGE_DICT = dict(_RARITY_PERCENTAGES)  # A dictionary of `rarity: percentage`

RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090  # Hot Pink
}

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
        "atlantic_sturgeon": "<:atlantic_sturgeon:878370649511432232>",
        "bluefin_notho": "<:bluefin_notho:878370648529969173>",
        "giant_sea_bass": "<:giant_sea_bass:878370648970387506>",
        "gold_doubloon_molly": "<:gold_doubloon_molly:878370648932626542>",
        "raccoon_butterflyfish": "<:raccoon_butterflyfish:878370649456922694>",
        "rainbow_kribensis_cichlid": "<:rainbow_kribensis_cichlid:878370648932638790>",
        "regal_blue_tang": "<:regal_blue_tang:878370650039918692>",
        "sea_goldie": "<:sea_goldie:878370649180106752>",
        "yellow_tang": "<:yellow_tang:878370649897328650>",
        "zebra_danios": "<:zebra_danios:878370648852922429>",
        "carp": "<:carp:878377327271227462>",
        "orca": "<:orca:878379352499310712>",
        "whale_shark": "<:whale_shark:878379353015197817>"
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
        "small_red_handfish": "<:small_red_handfish:878370649448534026>",
        "walking_batfish": "<:walking_batfish:878370649867960330>",
        "black_drakefish": "<:black_drakefish:878380261363056710>",
        "blue_drakefish": "<:blue_drakefish:878380261153329272>",
        "green_drakefish": "<:green_drakefish:878380261203644436>",
        "manatee": "<:manatee:878380626477211688>",
        "red_drakefish": "<:red_drakefish:878380261363036160>",
        "victory_drakefish": "<:victory_drakefish:878380261379825724>"
    },
    "rare": {
        "axolotl": "<:axolotl:878370649893109790>",
        "blobfish": "<:blobfish:878370649943441418>",
        "cuttlefish": "<:cuttlefish:878370649893109780>",
        "starfish_with_pants": "<:starfish_with_pants:878380007947386932>",
        "bobtail_squid": "<:bobtail_squid:878370649880543252>",
        "mantis_shrimp": "<:mantis_shrimp:878370649872146512>",
        "school_of_betta": "<:school_of_betta:878380008287133827>"
    },
    "epic": {
        "asian_arowana": "<:asian_arowana:878379497731276861>",
        "boesemani_rainbowfish": "<:boesemani_rainbowfish:878370649465311232>"
    },
    "legendary": {
        "anglerfish": "<:anglerfish:878379836064825354>"
    },
    "mythic": {
        "mandarinfish": "<:mandarinfish:878379851776679986>"
    }
}
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

COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
EPIC_BAG_NAMES = ["Epic Fish Bag", "Epic", "Efb"]
LEGENDARY_BAG_NAMES = ["Legendary Fish Bag", "Legendary", "Lfb"]
MYSTERY_BAG_NAMES = ["Mystery Fish Bag", "Mystery", "Mfb"]
FISH_FLAKES_NAMES = ["Fish Flakes", "Flakes", "Ff"]
FISH_BOWL_NAMES = ["Fish Bowl", "Bowl", "Fb"]
SMALL_TANK_NAMES = ["Small Tank", "Small", "St"]
MEDIUM_TANK_NAMES = ["Medium Tank", "Medium", "Mt"]
PLANT_LIFE_NAMES = ["Plant Life", "Plant", "Pl"]
FISH_REVIVAL_NAMES = ["Fish Revival", "Revival", "Fr"]


def special_percentage_finder(upgrade_level):
    return [
        list(i[0] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
        list(i[1] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
    ]


def rarity_percentage_finder(upgrade_level: int) -> typing.List[float]:
    """
    Gets a list of rarities for each level of commodity, per level.
    """

    return [
        list(i[0] for i in _RARITY_PERCENTAGES[upgrade_level]),
        list(i[1] for i in _RARITY_PERCENTAGES[upgrade_level]),
    ]


def parse_fish_filename(filename: str) -> dict:
    """
    Parse a given fish filename into a dict of `modifier`, `rarity`, `cost`,
    `raw_name`, and `name`.
    """

    # Initial filename splitterboi
    filename = filename[:-4]  # Remove file extension
    modifier = None
    rarity, cost, size, *raw_name = filename.split("_")

    # See if our fish name has a modifier on it
    if rarity in ["inverted", "golden"]:
        modifier, rarity, cost, size, raw_name = rarity, cost, size, raw_name[0], raw_name[1:]
    raw_name = "_".join(raw_name)

    # And we done
    return {
        "modifier": modifier,
        "rarity": rarity,
        "cost": cost,
        "size": size,
        "raw_name": raw_name,
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


def make_golden(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it golden.
    """

    fish["raw_name"] = f"golden_{fish['raw_name']}"
    fish["name"] = f"Golden {fish['name']}"
    fish["image"] = fish["image"][:40] + "golden_" + fish["image"][40:]
    return fish


def make_inverted(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it inverted.
    """

    fish["raw_name"] = f"inverted_{fish['raw_name']}"
    fish["name"] = f"Inverted {fish['name']}"
    fish["image"] = fish["image"][:40] + "inverted_" + fish["image"][40:]
    return fish


def get_normal_name(fish_name):
    """
    Get the non-inverted/golden name for the fish
    """
    match = re.match(r"(inverted_|golden_)(?P<fish_name>.*)", fish_name)
    if match:
        return match.group("fish_name")
    return fish_name
