from os import walk
import asyncio
from tokenize import _all_string_prefixes
import random
from datetime import datetime as dt, timedelta

import discord
from discord.ext import vbu

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
    0: 0.0010,
    1: 0.0020,
    2: 0.0040,
    3: 0.0080,
    4: 0.0150,
    5: 0.0300,
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
    ]


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


EMOJIS = {
    "achievement_star": "<:achievement_star:877646167087906816>",
    "achievement_star_new": "<:achievement_star_new:877737712046702592>",
    "achievement_star_no": "<:achievement_star_no:877646167222141008>",
    "amfc": "<:AMFC:913680729177751563>",
    "aqua_blep": "<:AquaBlep:878248090400870401>",
    "aqua_bonk": "<:AquaBonk:877722771935883265>",
    "aqua_cool": "<:AquaCool:878248090895802438>",
    "aqua_fish": "<:AquaFish:877939115948134442>",
    "aqua_love": "<:AquaLove:878248091201982524>",
    "aqua_pensive": "<:AquaPensive:877939116266909756>",
    "aqua_scared": "<:AquaScared:877939115943936074>",
    "aqua_shrug": "<:AquaShrug:877939116480802896>",
    "aqua_unamused": "<:AquaUnamused:877939116132696085>",
    "aqua_smile": "<:AquaSmile:877939115994255383>",
    "bar_1": "<:bar_1:877646167184408617>",
    "bar_2": "<:bar_2:877646166823694437>",
    "bar_3": "<:bar_3:877646167138267216>",
    "bar_e": "<:bar_e:877646167146643556>",
    "bar_empty": "<:__:886381017051586580>",
    "bar_L": "<:bar_L:886377903615528971>",
    "bar_L_branch": "<:bar_L_branch:886377903581986848>",
    "bar_L_straight": "<:bar_L_straight:886379040884260884>",
    "bar_R": "<:bar_R:877646167113080842>",
    "branch": "<:branch:886377903825252402>",
    "casts": "<:Casts:911465713938612235>",
    "common_fish_bag": "<:common_fish_bag:877646166983053383>",
    "doubloon": "<:doubloon:878297091057807400>",
    "experience_potion": "<:experience_potion:911465714412568616>",
    "feeding_potion": "<:feeding_potion:911465714379018261>",
    "fish_flake": "<:fish_flakes:877646167188602880>",
    "fish_pellet": "<:fish_pellets:911465714412552212>",
    "fish_points": "<:fish_points:911468089420427324>",
    "fish_wafer": "<:fish_wafers:911465714395799574>",
    "gfu": "<:GFU:913680729517469716>",
    "high_level_fish_bag": "<:high_level_fish_bag:912057609496985690>",
    "inverted_fish_bag": "<:inverted_fish_bag:912057608863637545>",
    "keep": "<:keep:844594468580491264>",
    "mutation_potion": "<:mutation_potion:911465714420949072>",
    "rare_fish_bag": "<:rare_fish_bag:877646167121489930>",
    "revival": "<:revival:878297091158474793>",
    "roll": "<a:roll:886068357378502717>",
    "sand_dollar": "<:sand_dollar:877646167494762586>",
    "sand_dollar_pile": "<:sand_dollar_pile:925288312611172372>",
    "sand_dollar_stack": "<:sand_dollar_stack:925288312418209853>",
    "sell": "<:sell:844594478392147968>",
    "straight": "<:straight:886377903879753728>",
    "straight_branch": "<:straight_branch:886377903837806602>",
    "uncommon_fish_bag": "<:uncommon_fish_bag:877646167146651768>",
    "pile_of_bottle_caps": "<:pile_of_bottle_caps:934600170274951188>",
    "plastic_bottle": "<:plastic_bottle:934600322305912904>",
    "plastic_bag": "<:plastic_bag:934600170228817930>",
    "seaweed_scraps": "<:seaweed_scraps:934604323399303239>",
    "broken_fishing_net": "<:broken_fishing_net:934600170346283038>",
    "halfeaten_flip_flop": "<:halfeaten_flipflop:934600169834577921>",
    "pile_of_straws": "<:pile_of_straws:934600169872306227>",
    "old_boot": "<:old_boot:934600170161717360>",
    "old_tire": "<:old_tire:934600169918439446>",
    "fishing_boots": "<:fishing_boots:957838977312907315>",
    "trash_toys": "<:trash_toys:957838977237397514>",
}

# List of names for tank themes
TANK_THEMES = PLANT_LIFE_NAMES

# Daylight savings variable because for some reason i need to
# add four and then an hour when its daylight savings,
# will be changed to 4 when daylight savings is over
DAYLIGHT_SAVINGS = 4

# What colors the embed should have based on rarity
RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090,  # Hot Pink
}


rarity_values = {
    "common": 5,
    "uncommon": 15,
    "rare": 75,
    "epic": 375,
    "legendary": 750,
    "mythic": 5000,
}
size_values = {
    "small": 1,
    "medium": 2,
    "large": 3,
}
skin_type_dict = {
    'ignited': ['neon_tetra_school', 'red_betta', 'koi', 'moon_jellyfish', 'sea_bunny', 'surge_wrasse'],
    'golden': ['clownfish', 'goldfish', 'guppies', 'headshield_slug', 'blue_maomao', 'bottlenose_dolphin',
               'pufferfish', 'starfish', 'tuna', 'anglerfish', 'bobtail_squid', 'blobfish',
               'cuttlefish', 'starfish_with_pants', 'dumbo_octopus', 'flowerhorn_cichlid', 'narwhal', 'smalltooth_sawfish'],
    'blooming': ['axolotl', 'sea_bunny'],
    'triumphant': ['omnifish', 'victory_drakefish', 'seal', 'shrimp', 'whale_shark', 'anglerfish']
}

location_list = []


class FishSpecies:

    all_species_by_name = {}
    all_species_by_rarity = {}
    all_fish_skins = {}

    def __init__(self, *, name: str, size: int, rarity: str, image: str, locations: list):
        self.name = name
        self.size = size
        self.rarity = rarity
        self.image = image
        self.locations = locations
        self.all_fish_skins[name] = ["inverted"]
        for skin_name, fish in skin_type_dict.items():
            if name in fish:
                self.all_fish_skins[name].append(skin_name)
        self.all_species_by_name[name] = self
        self.skins = self.all_fish_skins[name]
        if rarity not in self.all_species_by_rarity.keys():
            self.all_species_by_rarity[rarity] = [self]
        else:
            self.all_species_by_rarity[rarity].append(self)

    @classmethod
    def get_fish(cls, name: str):
        return cls.all_species_by_name[name]

    @classmethod
    def get_rarity(cls, rarity: str):
        return cls.all_species_by_rarity[rarity]

    @property
    def cost(self) -> int:
        return rarity_values[self.rarity] * size_values[self.size]


class Fish:

    def __init__(self, *, name: str, level: int, current_xp: int, max_xp: int, alive: bool, species: FishSpecies, location_caught: str, skin: str):
        self.name = name
        self.level = level
        self.current_xp = current_xp
        self.max_xp = max_xp
        self.alive = alive
        self.species = species
        self.location = location_caught
        self.skin = skin if skin else ""


def get_image(fish: Fish):
    if fish.skin != "":
        return f"{fish.species.image[:40]}{fish.skin}_{fish.species.image[40:]}"
    else:
        return fish.species.image


def get_normal_size_image(fish: Fish):
    if fish.skin != "":
        return f"{fish.species.image[:40]}{fish.skin}_fish_size{fish.species.image[44:]}"
    else:
        return f"{fish.species.image[:40]}normal_fish_size{fish.species.image[44:]}"


def parse_fish_filename(filename: str) -> dict:
    """
    Parse a given fish filename into a dict of `modifier`, `rarity`, `cost`,
    `raw_name`, and `name`.
    """

    # Initial filename splitterboi
    filename = filename[:-4]  # Remove file extension

    # Splits the formatted file name into its parts
    rarity, cost, size, *raw_name = filename.split("_")

    # Return the parts of the filename in a dict of the stats
    return rarity, size, "_".join(raw_name)


def fetch_fish(directory: str) -> dict:
    """
    Fetch all of the fish from a given directory.
    """

    # Set up a dict of fish the we want to append/return to
    fetched_fish = []

    # Grab all the filenames from the given directory
    _, _, fish_filenames = next(walk(directory))

    # Go through each filename
    for filename in fish_filenames:

        # Add the fish to the dict
        rarity, size, name = parse_fish_filename(filename)
        image = f"{directory}/{filename}"
        fetched_fish.append(
            FishSpecies(name=name, size=size, rarity=rarity, image=image, locations=location_list))

    return fetched_fish


'''
Trash stuff idk

    Collectibles:
        - Bottle Cap
            Chance: 15
        - Plastic Bottle
            Chance: 15
        - Plastic Bag
            Chance: 15
        - Seaweed
            Chance: 15
        - Fishing Net
            Chance: 10
        - Flip Flop
            Chance: 10
        - Straw
            Chance: 10
        - Old Boot
            Chance: 5
        - Tire
            Chance: 5

    Craftable:
        - DIY Cast
            Chance:
                1 in 80 casts
            Cost:
                2 Fishing Nets
            Gives:
                1 Cast

        - DIY Fish Bag
            Chance:
                1 on 88 casts
            Cost:
                2 Plastic Bags
                1 Straws
            Gives:
                1 Random Fish Bag

        - Fishing Boots
            Chance:
                1 in 280 casts
            Cost:
                2 Old Boots
                3 Fishing Nets
            Gives:
                5% chance of earning 2 casts instead of 1
                (Stacks, capping at 10)

        - DIY Toys
            Chance:
                1 in 456 casts
            Cost:
                2 Tires
                2 Flip Flops
                5 Plastic Bottles
                4 Seaweed
            Gives:
                1.50x bonus to xp earned from entertaining
                (Stacks, capping at 5)

'''

items_required = {
    "Cast": ({
        "broken_fishing_net": 2
    }, "Gives you one cast."),
    "Fish Bag": ({
        "plastic_bag": 2,
        "pile_of_straws": 1
    }, "Gives you one fish bag. (Either common, uncommon, or rare)"),
    "Fishing Boots": ({
        "old_boot": 2,
        "broken_fishing_net": 3
    }, "Gives you a 5% chance to get 2 casts instead of 1 each hour. (stacks up to 5)"),
    "Trash Toys": ({
        "old_tire": 2,
        "halfeaten_flip_flop": 2,
        "plastic_bottle": 5,
        "seaweed_scraps": 4
    }, "Gives you a 50% bonus to xp gotten from entertaining. (stacks up to 5)")
}


async def enough_to_craft(crafted: str, user_id: int):
    for item, required in items_required[crafted][0].items():
        async with vbu.Database() as db:
            amount = await db(f"""SELECT {item} FROM user_item_inventory WHERE user_id = $1""", user_id)
        if amount[0][item] < required:
            return False
    return True


async def create_select_menu(bot, ctx, option_list, type_noun, type_verb, remove=False):
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
    if remove == True:
        await message.delete()
    return str(payload.values[0])


async def create_modal(bot, Interaction, title, placeholder):
    """
    Modal
    """

    # Send a modal back to the user
    await Interaction.response.send_modal(
        (sent_modal := discord.ui.Modal(
            title=title,
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        label="Input text label",
                        style=discord.TextStyle.short,
                        placeholder=placeholder,
                        min_length=1,
                        max_length=32,
                    ),
                ),
            ],
        ))
    )

    # Wait for an interaction to be given back
    try:
        interaction: discord.Interaction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.data['custom_id'] == sent_modal.custom_id,
            timeout=60.0
        )
    except asyncio.TimeoutError:
        return None, None

    # Go through the response components and get the first (and only) value from the user
    assert interaction.components
    given_value = interaction.components[0].components[0].value

    # Respond with what the user said
    return given_value, interaction


def random_name_finder():
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
    return name


fish_footers = [
    '[Invite Aqua bot now](https://discord.com/oauth2/authorize?client_id=840956686743109652&scope=bot+applications.commands&permissions=52224)!',
    'Need help? Use the a.guide or join the [support server](https://discord.gg/FUyr8QmrD8)!',
    'Get a coding error message or some other error? Use a.bug `command name` `description` to report it!',
    'Vote for the bot with a.vote [(or here)](https://top.gg/bot/840956686743109652) to get access to a daily reward! (a.daily)',
    f'Join the [support server](https://discord.gg/FUyr8QmrD8) to get access to aqua emotes!',
    'Make sure you claim achievements with a.achievements to get doubloons!',
    'Make sure you\'re getting upgrades with the a.upgrades command!',
    'When using the a.buy command, put the item exactly as listen in parentheses, then the amount!',
    'Need to see a lot of information fast? use the a.profile command!',
    'Want to suggest something? fill out this [quick google form](https://forms.gle/ZFJitHwq8Kxasmt17)',
    'Get your first tank free with a.firsttank! (It only has room to hold one small fish)',
    'Make sure you take care of fish in tanks with the a.tank command!',
    'You can craft cool items using trash you catch with a.craft!',
    'To fish you need casts, which you get 6 for being new then 1 additional every hour'
]
# This is a list of fish that are no longer able to be caught
past_fish = ["acorn_goldfish", "cornucopish", "turkeyfish",
             "christmastreefish", "santa_goldfish", "gingerbread_axolotl"]
