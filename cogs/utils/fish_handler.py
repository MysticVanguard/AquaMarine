from os import walk
import re

SPECIAL_RARITY_PERCENTAGES = {
    1:
    [
        ("normal", .94),
        ("inverted", .05),
        ("golden", .01)
    ],
    2:
    [
        ("normal", .90),
        ("inverted", .08),
        ("golden", .02)
    ],
    3:
    [
        ("normal", .85),
        ("inverted", .12),
        ("golden", .03)
    ],
    4:
    [
        ("normal", .78),
        ("inverted", .18),
        ("golden", .04)
    ],
    5:
    [
        ("normal", .67),
        ("inverted", .27),
        ("golden", .06)
    ]
}

_RARITY_PERCENTAGES = {
    1:
    [
        ("common", 0.6689),
        ("uncommon", 0.2230),
        ("rare", 0.0743),
        ("epic", 0.0248),
        ("legendary", 0.0082),
        ("mythic", 0.0008),
    ],
    2:
    [
        ("common", 0.6062),
        ("uncommon", 0.2423),
        ("rare", 0.0967),
        ("epic", 0.0385),
        ("legendary", 0.0154),
        ("mythic", 0.0009),
    ],
    3:
    [
        ("common", 0.5156),
        ("uncommon", 0.2578),
        ("rare", 0.1289),
        ("epic", 0.0645),
        ("legendary", 0.0322),
        ("mythic", 0.0010),
    ],
    4:
    [
        ("common", 0.4558),
        ("uncommon", 0.2605),
        ("rare", 0.1490),
        ("epic", 0.0850),
        ("legendary", 0.0486),
        ("mythic", 0.0011),
    ],
    5:
    [
        ("common", 0.3843),
        ("uncommon", 0.2558),
        ("rare", 0.1701),
        ("epic", 0.1134),
        ("legendary", 0.0752),
        ("mythic", 0.0012),
    ]}

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

def special_percentage_finder(upgrade_level):
    return [
        list(i[0] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
        list(i[1] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
    ]

def rarity_percentage_finder(upgrade_level):
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
    fish["image"] = fish["image"][:16] + "golden_" + fish["image"][16:]
    return fish

def make_inverted(fish: dict) -> dict:
    """
    Take the given fish and change the dict to make it inverted.
    """

    fish["raw_name"] = f"inverted_{fish['raw_name']}"
    fish["name"] = f"Inverted {fish['name']}"
    fish["image"] = fish["image"][:16] + "inverted_" + fish["image"][16:]
    return fish

def make_pure(fish: dict, special: str) -> dict:
    """
    Take the given fish and change the dict to make it pure.
    """

    number = 0
    number_two = 16
    if special == "golden":
        number = 7
        number_two = 23
    elif special == "inverted":
        number = 9
        number_two = 25
    else:
        return
    fish["raw_name"] = fish['raw_name'][number:]
    fish["name"] = fish['name'][number:]
    fish["image"] = fish["image"][:16] + fish["image"][number_two:]
    return fish

def get_normal_name(self, fish_name):
    """
    Get the non-inverted/golden name for the fish
    """
    match = re.match(r"(inverted_|golden_)(?P<fish_name>.*)", fish_name)
    if match:
        return match.group("fish_name")
    return fish_name

