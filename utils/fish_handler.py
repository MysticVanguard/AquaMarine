from utils.load_config import config
from os import walk
import utils

_RARITY_PERCENTAGES = [
    ("common", 0.6689),
    ("uncommon", 0.2230),
    ("rare", 0.0743),
    ("epic", 0.0248),
    ("legendary", 0.0082),
    ("mythic", 0.0008),
]
RARITY_PERCENTAGE_DICT = dict(_RARITY_PERCENTAGES)  # A dictionary of `rarity: percentage`
RARITY_PERCENTAGE_LIST = [
    list(i[0] for i in _RARITY_PERCENTAGES),
    list(i[1] for i in _RARITY_PERCENTAGES),
]  # A nested list of `[[...rarity], [...percentage]]`
RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090  # Hot Pink
}


def parse_fish_filename(filename: str) -> dict:
    """
    Parse a given fish filename into a dict of `modifier`, `rarity`, `cost`,
    `raw_name`, and `name`.
    """

    # Initial filename splitterboi
    filename = filename[:-4]  # Remove file extension
    modifier = None
    rarity, cost, *raw_name = filename.split("_")

    # See if our fish name has a modifier on it
    if rarity in ["inverted", "golden"]:
        modifier, rarity, cost, raw_name = rarity, cost, raw_name[0], raw_name[1:]
    raw_name = "_".join(raw_name)

    # And we done
    return {
        "modifier": modifier,
        "rarity": rarity,
        "cost": cost,
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