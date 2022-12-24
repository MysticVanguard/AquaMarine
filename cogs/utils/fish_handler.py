from os import walk
import asyncio
import random
import discord
from discord.ext import vbu
from cogs import utils
import math

current_fishers = []

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

location_list = ['pond', 'estuary', 'creek', 'coral_reef',
                 'lake', 'river', 'deep_sea', 'ocean', 'none']

normalized_location_list = ["Pond", "Estuary", "Creek",
                            "Coral Reef", "Lake", "River", "Deep Sea", "Ocean"]


class FishSpecies:

    all_species_by_name = {}
    all_species_by_rarity = {}
    all_fish_skins = {}
    all_species_by_location_rarity = {}

    for location_type in location_list:
        all_species_by_location_rarity[location_type] = {
            "common": [], "uncommon": [], "rare": [], "epic": []}

    def __init__(self, *, name: str, size: int, rarity: str, image: str, location: str):
        self.name = name
        self.size = size
        self.rarity = rarity
        self.image = image
        self.location = location
        self.all_fish_skins[name] = ["inverted"]
        for skin_name, fish in skin_type_dict.items():
            if name in fish:
                self.all_fish_skins[name].append(skin_name)
        if rarity == 'mythic' and rarity not in self.all_species_by_location_rarity[location].keys():
            for location_type in location_list:
                self.all_species_by_location_rarity[location_type][rarity] = [
                    self]
        elif rarity not in self.all_species_by_location_rarity[location]:
            self.all_species_by_location_rarity[location][rarity] = [self]
        elif self.name not in [obj.name for obj in self.all_species_by_location_rarity[location][rarity]]:
            self.all_species_by_location_rarity[location][rarity].append(
                self)
        self.all_species_by_name[name] = self
        self.skins = self.all_fish_skins[name]
        if rarity not in self.all_species_by_rarity.keys():
            self.all_species_by_rarity[rarity] = [self]
        elif self.name not in [obj.name for obj in self.all_species_by_rarity[rarity]]:
            self.all_species_by_rarity[rarity].append(self)

    @classmethod
    def get_fish(cls, name: str):
        return cls.all_species_by_name[name]

    @classmethod
    def get_rarity(cls, rarity: str):
        return cls.all_species_by_rarity[rarity]

    @classmethod
    def get_location_rarity(cls, rarity: str, location: str) -> list:
        return cls.all_species_by_location_rarity[location][rarity]

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
    rarity, cost, size, *location_and_name = filename.split("_")

    # Return the parts of the filename in a dict of the stats
    for location_type in location_list:
        if location_and_name[0] == location_type:
            location = location_and_name[0]
            location_and_name.pop(0)
        elif "_".join(location_and_name[:2]) == location_type:
            location = "_".join(location_and_name[:2])
            location_and_name.pop(0)
            location_and_name.pop(0)
    return rarity, size, location, "_".join(location_and_name)


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
        rarity, size, location, name = parse_fish_filename(filename)
        image = f"{directory}/{filename}"
        fetched_fish.append(
            FishSpecies(name=name, size=size, rarity=rarity, image=image, location=location))

    return fetched_fish


def random_name_finder():
    titles = [
        "Captain", "Mr.", "Mrs.",
        "Commander", "Sir", "Madam",
        "Skipper", "Crewmate", "Lieutenant",
        "Privateer", "Portmaster", "Shipwright",
        "Commodore", "Rear Admiral", "Admiral",
        "Deckhand", "Cadet", "Sailor",
        "Boatswain", "Firstmate", "Quartermaster",
    ]
    names = [
        "Nemo", "Bubbles", "Jack",
        "Finley", "Coral", "Fish",
        "Turtle", "Squid", "Sponge",
        "Starfish", "Swedish", "McFish",
        "Floater", "Wave", "Chips",
        "Bob", "Cod", "Finneus",
        "Larry", "Salmon", "Sea Beast",
    ]
    name = f"{random.choice(titles)} {random.choice(names)}"
    return name


fish_footers = [
    '[Invite Aqua bot now](https://discord.com/oauth2/authorize?client_id=840956686743109652&scope=bot+applications.commands&permissions=52224)!',
    'Need help? Use the a.guide or join the [support server](https://discord.gg/FUyr8QmrD8)!',
    'Get a coding error message or some other error? Use a.bug `command name` `description` to report it!',
    'Vote for the bot with a.vote [(or here)](https://top.gg/bot/840956686743109652) to get access to a daily reward! (a.daily)',
    'Join the [support server](https://discord.gg/FUyr8QmrD8) to get access to aqua emotes!',
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
past_fish = ["acorn_goldfish", "cornucopish", "turkeyfish"]
# "christmastreefish", "santa_goldfish", "gingerbread_axolotl"


async def ask_to_sell_fish(
    bot, ctx, message: str, chosen_fish: FishSpecies, skin: str, embed, level_inserted: int = 0,
):
    """
    Ask the user if they want to sell a fish they've been given.
    """

    if skin != "":
        fish_file = discord.File(
            f"{chosen_fish.image[:40]}{skin}_{chosen_fish.image[40:]}", "new_fish.png")
    else:
        fish_file = discord.File(
            chosen_fish.image, "new_fish.png")
    size_demultiplier = {
        "small": 1,
        "medium": 2,
        "large": 3
    }
    # Add the buttons to the message
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(custom_id="keep", emoji=utils.EMOJIS["keep"]),
            discord.ui.Button(custom_id="sell", emoji=utils.EMOJIS["sell"]),
        ),
    )
    post_components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(label="Fish Again", custom_id="fish_again",
                              emoji=utils.EMOJIS["aqua_fish"]),
            discord.ui.Button(label="Stop", custom_id="stop")
        ),
    )
    message = await ctx.send(message, embed=embed, components=components, file=fish_file)

    async with bot.database() as db:
        fish_rows = await utils.user_fish_inventory_db_call(ctx.author.id)
        upgrades = await db(
            """SELECT rod_upgrade, weight_upgrade FROM user_upgrades WHERE user_id = $1""",
            ctx.author.id,
        )
        item_inventory = await utils.user_item_inventory_db_call(ctx.author.id)

    # Level variables
    level = (
        random.randint(
            utils.WEIGHT_UPGRADES[upgrades[0]["weight_upgrade"]][0],
            utils.WEIGHT_UPGRADES[upgrades[0]["weight_upgrade"]][1],
        )
        + level_inserted
    )

    # Wait for them to click a button
    returned_message = ""
    chosen_button_payload = None
    try:
        chosen_button_payload = await bot.wait_for(
            "component_interaction", timeout=60.0, check=lambda p: p.user.id == ctx.author.id)
        chosen_button = chosen_button_payload.component.custom_id.lower()
    except asyncio.TimeoutError:
        returned_message += "Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.\n"
        chosen_button = 'sell'

    # Update the displayed emoji
    if chosen_button == "keep":
        # Get their current fish names
        fish_names = [i["fish_name"] for i in fish_rows]
        xp_max = math.floor(25 * level ** 1.5)
        name, _ = await utils.create_modal(bot, chosen_button_payload, "Fish Kept", "Enter Your Fish's Name")
        while name in fish_names or not name:
            name = random_name_finder()
            while name in fish_names:
                name = random_name_finder()
            returned_message += f"{ctx.author.mention} An error occured! I'll name the fish for you!\n"
        returned_message += f"Your new fish **{name}** (Lvl. {level}) has been added to your bucket!"

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
    if chosen_button == "sell":
        # See if they want to sell the fish
        if chosen_button_payload:
            await chosen_button_payload.response.defer_update()
        vote_multiplier = 0
        if await utils.get_user_voted(bot, ctx.author.id):
            vote_multiplier = .5
            returned_message += "You voted at <https://top.gg/bot/840956686743109652/vote> for a **1.5x** bonus"
        level_multiplier = level / 20
        money_gained = int(chosen_fish.cost /
                           size_demultiplier[chosen_fish.size])
        money_earned = math.ceil((money_gained) * (
            utils.ROD_UPGRADES[upgrades[0]["rod_upgrade"]] + level_multiplier + vote_multiplier))

        async with bot.database() as db:
            if item_inventory[0]["recycled_fishing_rod"] > 0:
                money_earned *= 2
                await db("""UPDATE user_item_inventory SET recycled_fishing_rod = recycled_fishing_rod - 1 WHERE user_id = $1""",
                         ctx.author.id)
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
        returned_message += f"Sold your **{chosen_fish.name.replace('_', ' ').title()}** for **{money_earned}** {utils.EMOJIS['sand_dollar']}!"
    await message.edit(components=components.disable_components())
    await message.delete(delay=5)
    return returned_message, post_components

user_last_fish_caught = {}


async def user_fish(self, ctx, casts, upgrades, user_locations_info, user_inventory, location_pools_info):

    # pick a random number using the line upgrade, if it is equal to 1 they get to fish twice
    caught_fish = 1
    two_in_one_roll = random.randint(
        1, utils.LINE_UPGRADES[upgrades[0]["line_upgrade"]]
    )
    # if two_in_one_roll == 1:
    #    caught_fish = 2

    # If they didn't catch trash
    if random.randint(1, 10) != 10:

        # For each fish caught...
        for _ in range(caught_fish):

            async with vbu.Database() as db:
                user_items = await utils.user_item_inventory_db_call(ctx.author.id)
            # Use upgrades for chances of rarity and mutation, and choose one with weighted randomness
            rarity = random.choices(
                *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
            )[0]
            while rarity not in FishSpecies.all_species_by_location_rarity[user_locations_info[0]['current_location']].keys() or (user_items[0]["recycled_bait"] > 0 and rarity == "common"):
                rarity = random.choices(
                    *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                )[0]
            if user_items[0]["recycled_fish_hook"] > 0:
                special = random.choices(("normal", "skinned"), (.75, .25))[0]
            else:
                special = random.choices(("normal", "skinned"),
                                         (1-utils.LURE_UPGRADES[upgrades[0]["lure_upgrade"]],
                                          utils.LURE_UPGRADES[upgrades[0]["lure_upgrade"]])
                                         )[0]

            # See which fish they caught by taking a random fish from the chosen rarity)
            if ctx.author.id not in utils.user_last_fish_caught.keys():
                utils.user_last_fish_caught[ctx.author.id] = ""

            chosen_fish = random.choice(
                FishSpecies.get_location_rarity(
                    rarity, user_locations_info[0]['current_location'])
            )
            while chosen_fish.name in utils.past_fish or location_pools_info[0][f"{chosen_fish.name}_count"] <= 0 or chosen_fish.name == utils.user_last_fish_caught[ctx.author.id]:
                rarity = random.choices(
                    *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                )[0]
                while rarity not in FishSpecies.all_species_by_location_rarity[user_locations_info[0]['current_location']].keys() or (user_items[0]["recycled_bait"] > 0 and rarity == "common"):
                    rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                chosen_fish = random.choice(
                    FishSpecies.get_location_rarity(
                        rarity, user_locations_info[0]['current_location'])
                )
            if user_items[0]["recycled_fish_finder"] > 0:
                species = FishSpecies.get_location_rarity(
                    rarity, user_locations_info[0]["current_location"])
                new_fish = await utils.create_select_menu(self.bot, ctx, [fish_type.name for fish_type in species], "fish", "catch", True)
                if new_fish:
                    chosen_fish = FishSpecies.get_fish(new_fish)
            utils.user_last_fish_caught[ctx.author.id] = chosen_fish.name
            # If the fish is skinned, choose one of it's skins
            fish_skin = ""
            if special == "skinned":
                fish_skin = random.choice(chosen_fish.skins)

            # Grammar
            a_an = (
                "an" if chosen_fish.name[0].lower() in (
                    "a", "e", "i", "o", "u") else "a"
            )

            # Get their fish inventory, add 1 to their times caught in achievements, subtract 1 from their casts
            async with vbu.Database() as db:
                if user_items[0]["recycled_bait"] > 0:
                    await db("""UPDATE user_item_inventory SET recycled_bait = recycled_bait - 1 WHERE user_id = $1""",
                             ctx.author.id)
                if user_items[0]["recycled_fish_hook"] > 0:
                    await db("""UPDATE user_item_inventory SET recycled_fish_hook = recycled_fish_hook - 1 WHERE user_id = $1""",
                             ctx.author.id)
                if user_items[0]["recycled_fish_finder"] > 0:
                    await db("""UPDATE user_item_inventory SET recycled_fish_finder = recycled_fish_finder - 1 WHERE user_id = $1""",
                             ctx.author.id)
                await db(
                    f"""UPDATE user_location_info SET {chosen_fish.name}_caught = {chosen_fish.name}_caught + 1 WHERE user_id = $1""",
                    ctx.author.id,
                )
                # Achievements
                await db(
                    """UPDATE user_achievements SET times_caught = times_caught + 1 WHERE user_id = $1""",
                    ctx.author.id,
                )
                await db(
                    """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                    ctx.author.id,
                )
                await db(
                    f"""UPDATE fish_pool_location SET {chosen_fish.name}_count = {chosen_fish.name}_count - 1"""
                )

            # Find out how many of those fish they caught previously
            amount = user_locations_info[0][f"{chosen_fish.name}_caught"]

            # Set the fish file to the fishes image
            if fish_skin != "":
                skin_name = fish_skin
                fish_file = discord.File(
                    f"{chosen_fish.image[:40]}{fish_skin}_{chosen_fish.image[40:]}", "new_fish.png")
            else:
                skin_name = "None"
                fish_file = discord.File(
                    chosen_fish.image, "new_fish.png")

            # Add the fish caught's name to the choices
            choices = [chosen_fish.name.replace('_', ' ').title()]

            # For three other fish...
            for _ in range(3):

                # Get a random other fish
                random_rarity = random.choices(
                    *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                )[0]
                random_fish = random.choice(
                    utils.FishSpecies.get_rarity(random_rarity))

                # If it's already a choice find a new one
                while random_fish.name.replace('_', ' ').title() in choices:
                    random_rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                    random_fish = random.choice(
                        utils.FishSpecies.get_rarity(random_rarity))

                # Add that fish to the choices
                choices.append(
                    random_fish.name.replace('_', ' ').title())

            # Shuffle the choices so they're random
            random.shuffle(choices)

            # And send the choices as buttons
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=choices[0], custom_id=choices[0]
                    ),
                    discord.ui.Button(
                        label=choices[1], custom_id=choices[1]
                    ),
                    discord.ui.Button(
                        label=choices[2], custom_id=choices[2]
                    ),
                    discord.ui.Button(
                        label=choices[3], custom_id=choices[3]
                    ),
                ),
            )

            # Sends the message with the pic of fish and buttons
            guess_ask_message = await ctx.send(f"{utils.EMOJIS['aqua_shrug']}Guess The Species:", file=fish_file, components=components)

            # Make the button check
            def guess_button_check(payload):
                # The correct message
                if payload.message.id != guess_ask_message.id:
                    return False
                if payload.component.custom_id not in choices:
                    return False
                return payload.user.id == ctx.author.id

            # Wait for them to click a button
            try:
                guess_chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60, check=guess_button_check
                )
                chosen_button = (
                    guess_chosen_button_payload.component.custom_id
                )
            except asyncio.TimeoutError:
                chosen_button = "AAAAA"

            # Give them a bonus based on the fish's cost and tell them they got it correct if they did
            await guess_ask_message.delete()
            if chosen_button == chosen_fish.name.replace('_', ' ').title():
                bonus = 15 + math.floor(int(chosen_fish.cost) / 10)
                guess_message = f"{utils.EMOJIS['aqua_love']} <@{ctx.author.id}> guessed correctly and recieved a bonus of {bonus} {utils.EMOJIS['sand_dollar']}!"

                # Update the users balance with the bonus
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
                        ctx.author.id,
                        bonus,
                    )

            # Else tell them it was wrong
            else:
                guess_message = f"{utils.EMOJIS['aqua_pensive']} Incorrect <@{ctx.author.id}>, no bonus given."

            # Tell the user about the fish they caught
            owned_unowned = "Owned" if amount > 0 else "Unowned"
            embed = discord.Embed(
                title=f"{utils.EMOJIS['aqua_fish']} {ctx.author.display_name} caught {a_an} **{chosen_fish.name.replace('_', ' ').title()}**!"
            )
            embed.add_field(name="Rarity:", value=rarity)
            embed.add_field(name="Size:", value=chosen_fish.size)
            embed.add_field(name="Skin:", value=skin_name)
            embed.add_field(
                name=owned_unowned,
                value=f"You have caught {amount} **{chosen_fish.name.replace('_', ' ').title()}**",
                inline=False,
            )
            embed.set_image(url="attachment://new_fish.png")
            embed.add_field(
                name="** **", value=f"*{random.choice(utils.fish_footers)}*")
            embed.color = utils.RARITY_CULERS[rarity]
            if casts[0]["casts"] == 3:
                guess_message += "\n⚠️You have two casts left⚠️"
            # Ask if they want to sell the fish they just caught or keep it
            return await utils.ask_to_sell_fish(self.bot, ctx, guess_message, chosen_fish, fish_skin, embed=embed)

    # Else if they catch trash...
    else:
        # Still use up a cast
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                ctx.author.id,
            )

        # Initiate the trash dict and string
        trash_dict = {}
        trash_string = ""

        # For each trash caught (1-6)...
        for i in range(random.randint(1, 6)):

            # They catch a random weighted trash
            caught = random.choices(
                (
                    "Pile Of Bottle Caps",
                    "Plastic Bottle",
                    "Plastic Bag",
                    "Seaweed Scraps",
                    "Broken Fishing Net",
                    "Halfeaten Flip Flop",
                    "Pile Of Straws",
                    "Old Boot",
                    "Old Tire"
                ),
                (
                    .15,
                    .15,
                    .15,
                    .15,
                    .1,
                    .1,
                    .1,
                    .05,
                    .05,
                )
            )[0]

            # If its not already in the dict add it with a 1, else add 1 to it
            if caught not in trash_dict.keys():
                trash_dict[caught] = 1
            else:
                trash_dict[caught] += 1

        # for each type of trash...
        for trash, amount in trash_dict.items():

            # Add that trash to a string
            trash_string += "\n" + \
                f"{utils.utils.EMOJIS[trash.replace(' ', '_').lower()]}{trash}: {amount}"

            # Add the trash to their inventory
            async with vbu.Database() as db:
                await db(
                    f"""UPDATE user_item_inventory SET {trash.replace(' ', '_').lower()} = {trash.replace(' ', '_').lower()}+ {amount} WHERE user_id = $1""",
                    ctx.author.id,
                )

        post_components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="Fish Again", custom_id="fish_again",
                                  emoji=utils.EMOJIS["aqua_fish"]),
                discord.ui.Button(label="Stop", custom_id="stop")
            ),
        )
        # Tell them they caught trash and how much of what types
        return f"{utils.EMOJIS['aqua_trash']} You caught trash!{trash_string}", post_components
