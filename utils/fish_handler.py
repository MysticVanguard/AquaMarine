from utils.load_config import config
from os import walk
import utils
import discord
import asyncio




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
def rarity_percentage_finder(upgrade_level):
    return [
    list(i[0] for i in _RARITY_PERCENTAGES[upgrade_level]),
    list(i[1] for i in _RARITY_PERCENTAGES[upgrade_level]),
]
def special_percentage_finder(upgrade_level):
    return [
    list(i[0] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
    list(i[1] for i in SPECIAL_RARITY_PERCENTAGES[upgrade_level]),
]
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


def fetch_fish(directory: str = config["assets"]["images"]["fish"]) -> dict:
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

async def check_price( user_id: int, cost: int) -> bool:
    """
    Returns if a user_id has enough money based on the cost.
    """
    async with utils.DatabaseConnection() as db:
        user_rows = await db(
            """SELECT balance FROM user_balance WHERE user_id=$1""",
            user_id,
        )
        user_balance = user_rows[0]['balance']
    return user_balance >= cost

async def buying_singular(ctx, item: str):
    """
    For Buying a singular item such as a tank or theme
    """
    # Variables for possible inputs
    tanks = ["Fish Bowl", "Small Tank", "Medium Tank"]
    themes = ["Plant Life"]

    # Gets the tank info for user
    async with utils.DatabaseConnection() as db:
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
            async with utils.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank[$1] = TRUE, tank_type[$1] = $2, tank_name[$1]=$3, fish_room[$1]=$4, tank_theme[$1]='Aqua' WHERE user_id=$5""", int(message), item, name, tank_size_values[item], ctx.author.id)
        else:

            # If the tank is just updating a tank, updates the tank
            await ctx.send(f"Tank {tank_names[int(message)-1]} has been updated to {item}!")
            async with utils.DatabaseConnection() as db:
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
        async with utils.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank_theme[$1] = $2 WHERE user_id=$3""", tank_names.index(theme_message), item.replace(" ", "_"), ctx.author.id)

