from datetime import timedelta
import collections
import asyncio
import random
import string

from PIL import Image
import discord
from discord.ext import commands, vbu

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS
from cogs.utils import EMOJIS

# Set up the credits embed
CREDITS_EMBED = discord.Embed(
    title="Credits to all the people who have helped make this bot what it is!"
)
CREDITS_EMBED.add_field(
    name="The lovely coders who helped me with creating the bot, and who have taught me so much!",
    value="""
        [**Hero#2313**](https://github.com/iHeroGH): Creator of StalkerBot
        [**Kae#0004**](https://voxelfox.co.uk/): Creator of MarriageBot and so many others
        [**slippery schlöpp#6969**](https://github.com/schlopp): Creator of pp bot
    """,
    inline=False,
)
CREDITS_EMBED.add_field(
    name="Credits to the wonderful Peppoco (peppoco#6867), who made these lovely emotes!",
    value=EMOJIS["aqua_bonk"]
    + EMOJIS["aqua_pensive"]
    + EMOJIS["aqua_fish"]
    + EMOJIS["aqua_scared"]
    + EMOJIS["aqua_shrug"]
    + EMOJIS["aqua_smile"]
    + EMOJIS["aqua_unamused"]
    + EMOJIS["aqua_love"]
    + EMOJIS["aqua_cool"]
    + EMOJIS["aqua_blep"]
    + "(https://peppoco.carrd.co/#)",
    inline=False,
)
CREDITS_EMBED.add_field(
    name="Credits to all the people who have helped me test the bot!",
    value="""
        Aria, Astro, Dessy, Finn, George,
        Jack, Kae, Nafezra, Quig Quonk,
        Schlöpp, Toby, Victor, Ween
    """,
    inline=False,
)


class Informative(vbu.Cog):
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        """
        Shows information about the user's tanks.
        """

        # Set up the prefix for any images we need to access
        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"

        # A dict of tank types
        tank_types = {
            "Fish Bowl": "fishbowl",
            "Small Tank": "Small_Tank_2D",
            "Medium Tank": "Medium_Tank_2D",
        }

        # A dict of the positions of where glass should go for each type of tank in each spot
        position_glass = {
            "Fish Bowl": [
                (390, 160),
                (1470, 160),
                (2510, 160),
                (390, 640),
                (1470, 640),
                (2510, 640),
                (950, 1170),
                (1970, 1170),
                (950, 1540),
                (1970, 1540),
            ],
            "Small Tank": [
                (350, 40),
                (1400, 40),
                (2450, 40),
                (350, 520),
                (1400, 520),
                (2450, 520),
                (890, 1050),
                (1900, 1050),
                (809, 1440),
                (1900, 1440),
            ],
            "Medium Tank": [
                (240, 40),
                (1290, 40),
                (2340, 40),
                (240, 520),
                (1290, 520),
                (2340, 520),
                (770, 1050),
                (1780, 1050),
                (770, 1440),
                (1780, 1440),
            ],
        }

        # A dict of the positions of where themes should go for each type of tank in each spot
        position_theme = {
            "Fish Bowl": [
                (390, 160),
                (1470, 160),
                (2510, 160),
                (390, 640),
                (1470, 640),
                (2510, 640),
                (950, 1170),
                (1970, 1170),
                (950, 1540),
                (1970, 1540),
            ],
            "Small Tank": [
                (360, 70),
                (1410, 70),
                (2460, 70),
                (360, 550),
                (1410, 550),
                (2460, 550),
                (900, 1080),
                (1910, 1080),
                (900, 1470),
                (1910, 1470),
            ],
            "Medium Tank": [
                (250, 70),
                (1300, 70),
                (2350, 70),
                (250, 550),
                (1300, 550),
                (2350, 550),
                (780, 1080),
                (1790, 1080),
                (780, 1470),
                (1790, 1470),
            ],
        }

        # Random ID for what the tank will be saved as
        id = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(10)
        )

        # Set the unique file name for the wall
        file_name = f"{file_prefix}/background/Room Walls/Tanks_Wall/User Walls/{id}user_tank_room.png"

        # Get the user's data
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1""",
                ctx.author.id,
            )
            tank_rows = await db(
                """SELECT * FROM user_tank_inventory WHERE user_id = $1""",
                ctx.author.id,
            )

        # Open the background image for tanks to be pasted onto and copy it
        background = Image.open(
            f"{file_prefix}/background/Room Walls/Tank_Wall-export.png"
        ).convert("RGBA")
        new_background = background.copy()

        # For each tank...
        for slot, tank in enumerate(tank_rows[0]["tank_type"]):

            # If theres nothing dont change anything
            if tank == "":
                continue

            # Set start and theme_raise to 0 for tanks under the counter
            start = ""
            theme_raise = 0

            # If its a medium or small tank and in the spots under the counter
            if (tank == "Medium Tank" or tank == "Small Tank") and slot in [
                10,
                11,
            ]:
                # Change the start and the raise of the theme
                start = "Under_"
                theme_raise = 2

            # Set the type to what it is, the positions of the glass and theme to what they are, and the theme to what it is for this tank
            tank_type = tank_types[tank]
            x_and_y_glass = position_glass[tank][slot]
            x_and_y_theme = position_theme[tank][slot]
            if tank_rows:
                tank_theme = tank_rows[0]["tank_theme"][slot].replace(" ", "_")

            # Open the glass and theme images
            glass = Image.open(
                f"{file_prefix}/background/Room Walls/Tanks_Wall/{start}Glass_{tank_type}-export.png"
            ).convert("RGBA")
            theme = Image.open(
                f"{file_prefix}/background/Room Walls/Tanks_Wall/{tank_theme}_{tank_type}-export.png"
            ).convert("RGBA")

            # Paste them on top of the background
            new_background.paste(
                theme, (x_and_y_theme[0], x_and_y_theme[1]), theme
            )
            new_background.paste(
                glass,
                (x_and_y_glass[0], x_and_y_glass[1] - theme_raise),
                glass,
            )

        # save the file as a png
        new_background.save(file_name, format="PNG")

        # Send the file
        await ctx.send(file=discord.File(file_name))

        # Set up some vars for later
        embed = discord.Embed()
        fish_collections = collections.defaultdict(list)

        # For each of the users fish
        for fish in fish_row:

            # if the fish is in a tank
            if fish["tank_fish"] != "":

                # Find the time it dies
                relative_time = discord.utils.format_dt(
                    fish["death_time"] - timedelta(hours=DAYLIGHT_SAVINGS),
                    style="R",
                )

                # Find all the relevant data for the fish
                fish_collections[fish["tank_fish"]].append(
                    f"**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**\n"
                    f"{EMOJIS['bar_empty']}Alive: **{fish['fish_alive']}**\n"
                    f"{EMOJIS['bar_empty']}Death Date: **{relative_time}**\n"
                    f"{EMOJIS['bar_empty']}Level: **{fish['fish_level']}**\n"
                    f"{EMOJIS['bar_empty']}XP: **{fish['fish_xp']}/{fish['fish_xp_max']}**"
                )

        # Check for if they have no tanks
        if not tank_rows:
            return await ctx.send("You have no tanks!")

        # Set up the fields
        field = []

        # For each tank...
        for tank_row in tank_rows:
            for count in range(len(tank_row["tank"])):

                # If the tank name is in the unique dict of tanks keys
                if tank_row["tank_name"][count] in fish_collections.keys():

                    # set up the fish message to be all the fish data
                    fish_message = [
                        "\n".join(
                            fish_collections[tank_row["tank_name"][count]]
                        )
                    ]

                # Else make the fish message say theres no fish
                else:
                    fish_message = ["No fish in tank."]

                # as long as theres a tank
                if tank_row["tank"][count] is True:

                    # Make sure theres a fish message
                    if not fish_message:
                        fish_message = ["No fish in tank."]

                    # append the tank name and type with the fish_message
                    field.append(
                        (
                            f"{tank_row['tank_name'][count]} (Tank Type: {tank_row['tank_type'][count]})",
                            "\n".join(fish_message),
                        )
                    )

        # Make sure the fields are the correct length
        fields = []
        for field_single in field:
            [fields.append(i) for i in utils.get_fixed_field(field_single)]

        # Send the embed with the tank data
        await utils.paginate(
            ctx, fields, ctx.author, f"{ctx.author.display_name}'s tanks"
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def profile(self, ctx: commands.Context):
        """
        Shows the user's profile.
        """

        # Set up the new line variable for f strings
        n = "\n"

        # Dict of all the items and their emoji
        items = {
            "cfb": EMOJIS["common_fish_bag"],
            "ufb": EMOJIS["uncommon_fish_bag"],
            "rfb": EMOJIS["rare_fish_bag"],
            "ifb": EMOJIS["inverted_fish_bag"],
            "hlfb": EMOJIS["high_level_fish_bag"],
            "flakes": EMOJIS["fish_flake"],
            "pellets": EMOJIS["fish_pellet"],
            "wafers": EMOJIS["fish_wafer"],
            "revival": EMOJIS["revival"],
            "feeding_potions": EMOJIS["feeding_potion"],
            "experience_potions": EMOJIS["experience_potion"],
            "mutation_potions": EMOJIS["mutation_potion"],
            "pile_of_bottle_caps": EMOJIS["pile_of_bottle_caps"],
            "plastic_bottle": EMOJIS["plastic_bottle"],
            "plastic_bag": EMOJIS["plastic_bag"],
            "seaweed_scraps": EMOJIS["seaweed_scraps"],
            "broken_fishing_net": EMOJIS["broken_fishing_net"],
            "halfeaten_flip_flop": EMOJIS["halfeaten_flip_flop"],
            "pile_of_straws": EMOJIS["pile_of_straws"],
            "old_boot": EMOJIS["old_boot"],
            "old_tire": EMOJIS["old_tire"],
        }

        # Set up the default values
        tank_string = f"{n}{n}**# of tanks**{n}none"
        balance_string = f"{n}{n}**Balance**{n}none"
        collection_string = "none"
        highest_level_fish_string = "none"
        items_string = "none"

        # Get the user's inventory from the database
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1""",
                ctx.author.id,
            )
            tank_row = await db(
                """SELECT * FROM user_tank_inventory WHERE user_id = $1""",
                ctx.author.id,
            )
            balance = await db(
                """SELECT * FROM user_balance WHERE user_id = $1""",
                ctx.author.id,
            )
            inventory_row = await db(
                """SELECT * FROM user_item_inventory WHERE user_id = $1""",
                ctx.author.id,
            )

        # If theres a tank row
        if tank_row:

            # Get the number of tanks that the user has
            number_of_tanks = 0
            if tank_row:
                number_of_tanks = tank_row[0]["tank"].count(True)
            tank_string = f"{n}{n}**# of tanks**{n}{number_of_tanks}"

        # If theres a fish row
        if fish_row:

            # Get a list of the user's fish types and levels
            user_fish = []
            user_fish_info = []
            for row in fish_row:
                user_fish.append(row["fish"])
                user_fish_info.append(row["fish_level"])

            # Work out the user's highest level fish
            highest_level_index = user_fish_info.index(max(user_fish_info))
            highest_level_fish = fish_row[highest_level_index]
            highest_level_fish_string = f' {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}'

            # Find each fish type the user has and create the collection data list
            collection_data = []
            user_fish_types = {i["fish"] for i in fish_row}

            # For eaach rarity...
            for rarity, fish in self.bot.fish.items():

                # Find the amount of fish in that rarity
                rarity_fish_count = len(fish)

                # Set the user's count to 0
                user_rarity_fish_count = 0

                # For each fish if the user owns one add 1 to the count
                for info in fish.values():
                    if info["raw_name"] in user_fish_types:
                        user_rarity_fish_count += 1

                # Add that data to the collection data list
                collection_data.append(
                    [rarity, rarity_fish_count, user_rarity_fish_count]
                )

            # Set the collection info in the correct format
            collection_string = '\n'.join(
                f"{x[0]}: {x[2]}/{x[1]}" for x in collection_data)

        # If there are items
        if inventory_row:

            # Initiate the number dict and count
            inventory_number = {}
            count = 0

            # For each type of item...
            for key, value in inventory_row[0].items():

                # if its the user_id skip it
                if key == "user_id":
                    continue

                # Every three add a new line to the key and add it to the value
                if (count % 3) == 0 and count != 0:
                    inventory_number[("\n" + (items[key]))] = str(value)
                else:
                    inventory_number[items[key]] = value

                # Accumulator
                count += 1

            # Make the inventory info formated
            inventory_info = [
                f"{inv_key}: x{inv_value}"
                for inv_key, inv_value in inventory_number.items()
            ]

            # Make the items key have the inventory and balance
            items_string = " ".join(inventory_info)

        # format the user's balance if it exists
        if balance:
            balance_string = (
                f"{n}{n}**Balance**{n}"
                f'{EMOJIS["sand_dollar"]}: x{balance[0]["balance"]}   '
                f'{EMOJIS["doubloon"]}: x{balance[0]["doubloon"]}{n}'
                f'{EMOJIS["casts"]}: x{balance[0]["casts"]}   '
                f'{EMOJIS["fish_points"]}: x{balance[0]["extra_points"]}'
            )

        # Set up the fields
        fields_dict = {
            "Highest Level Fish": (highest_level_fish_string, False),
            "Collection": (collection_string + tank_string, True),
            "Items": (items_string + balance_string, True),
        }

        # Create and format the embed
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s Profile")
        embed.set_thumbnail(url="https://i.imgur.com/lrqPSgF.png")
        for name, (text, inline) in fields_dict.items():
            embed.add_field(name=name, value=text, inline=inline)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx: commands.Context, *, fish_name: str = None):
        """
        This command shows the user info about fish.
        """

        # If we want to just send all the fish
        if not fish_name:

            # Set up the fields
            fields = []

            # For each rarity
            for rarity, fish_types in self.bot.fish.items():

                # Set up the field and string for that rarity
                fish_lines = []
                fish_string = ""

                # For each fish in the types
                for count, fish_type in enumerate(fish_types.keys()):

                    # Every other fish either bold or codeblock the text for contrast
                    if count % 2 == 0:
                        fish_string += f" | **{' '.join(fish_type.split('_')).title()}**"
                    else:
                        fish_string += f" | `{' '.join(fish_type.split('_')).title()}`"

                    # Every three append it to the lines and reset the string
                    if (count + 1) % 3 == 0:
                        fish_lines.append(fish_string)
                        fish_string = ""

                    # If its the last one and not filled up to three append anyways
                    if (count + 1) == len(fish_types.keys()):
                        fish_lines.append(fish_string)

                # set the field to equal the lines joined by newlines and fix the fields up
                field = (rarity.title(), "\n".join(fish_lines))
                [fields.append(i) for i in utils.get_fixed_field(field)]

            # Send the fields paginated
            return await utils.paginate(
                ctx, fields, ctx.author, "**Bestiary**\n"
            )

        # If a fish is specified...

        # If they specified inverted, replace it and set the check to true
        inverted = False
        if "inverted" in fish_name.lower():
            fish_name = fish_name.replace("inverted ", "")
            inverted = True

        # Find the info of the fish they selected
        selected_fish = None
        for rarity, fish_types in self.bot.fish.items():
            for _, fish_info in fish_types.items():
                if fish_info["name"] == str(fish_name.title()):
                    selected_fish = fish_info
                    break
            if selected_fish:
                break

        # If it doesnt exist tell them
        else:
            return await ctx.send("That fish doesn't exist.")

        # If its inverted change the fish's info to be inverted
        if inverted is True:
            utils.make_inverted(selected_fish)

        # Set up the embed with all the needed data
        embed = discord.Embed(title=selected_fish["name"])
        embed.set_image(url="attachment://new_fish.png")
        embed.add_field(
            name="Rarity:", value=f"{selected_fish['rarity']}", inline=True
        )
        embed.add_field(
            name="Base Sell Price:",
            value=f"{int(selected_fish['cost'])} {EMOJIS['sand_dollar']}",
            inline=True,
        )
        embed.add_field(
            name="Size:", value=f"{selected_fish['size']}", inline=True
        )
        embed.color = {
            "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
            "uncommon": 0x75FE66,  # Green
            "rare": 0x4AFBEF,  # Blue
            "epic": 0xE379FF,  # Light Purple
            "legendary": 0xFFE80D,  # Gold
            "mythic": 0xFF0090,  # Hot Pink
        }[selected_fish["rarity"]]
        fish_file = discord.File(selected_fish["image"], "new_fish.png")

        # Send the embed
        await ctx.send(file=fish_file, embed=embed)

    @commands.command(aliases=["bucket", "fb"])
    @commands.bot_has_permissions(
        send_messages=True, embed_links=True, manage_messages=True
    )
    async def fishbucket(
        self, ctx: commands.Context, user: discord.User = None
    ):
        """
        Show a user's fishbucket.
        """

        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

        # Default the user to the author of the command
        user = user or ctx.author

        # Get the fish information
        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish=''""",
                user.id,
            )
        if not fish_rows:
            if user == ctx.author:
                return await ctx.send("You have no fish in your bucket!")
            return await ctx.send(
                f"**{user.display_name}** has no fish in their bucket!"
            )

        # Find the fish's data in a list of tuples sorted
        fish_list = [
            (i["fish_name"], i["fish"], i["fish_alive"]) for i in fish_rows
        ]
        fish_list = sorted(fish_list, key=lambda x: x[1])

        # The "pages" that the user can scroll through are the different rarity levels
        fields = (
            []
        )

        # Dictionary of the fish that the user has
        sorted_fish = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": [],
            "legendary": [],
            "mythic": [],
        }

        # Sorted Fish will become a dictionary of {rarity: [list of fish names of fish in that category]} if the fish is in the user's inventory
        for (
            rarity,
            fish_types,
        ) in self.bot.fish.items():  # For each rarity level
            for (
                _,
                fish_detail,
            ) in fish_types.items():  # For each fish in that level
                raw_name = fish_detail["raw_name"]
                for user_fish_name, user_fish, alive in fish_list:

                    # If the fish in the user's list matches the name of a fish in the rarity catgeory
                    if raw_name == utils.get_normal_name(user_fish):

                        # Append to the dictionary
                        sorted_fish[rarity].append(
                            (
                                user_fish_name,
                                user_fish,
                                fish_detail["size"],
                                alive,
                            )
                        )

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [
                    f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}** (Size: {fish_size.title()}, Alive: {alive})"
                    for fish_name, fish_type, fish_size, alive in fish_list
                ]
                field = (rarity.title(), "\n".join(fish_string))
                [fields.append(i) for i in utils.get_fixed_field(field)]

        # Create an embed
        await utils.paginate(ctx, fields, user)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def achievements(self, ctx: commands.Context):
        """
        Shows the achievements and lets the user claim them.
        """

        # The milestones for each achievement type
        milestones_dict_of_achievements = {
            "times_entertained": [
                96,
                672,
                1344,
                2880,
                8640,
                17280,
                25920,
                35040,
                52512,
                70080,
            ],
            "times_fed": [
                1,
                10,
                50,
                100,
                1500,
                3000,
                6000,
                22750,
                34125,
                45500,
            ],
            "times_cleaned": [
                12,
                84,
                168,
                360,
                540,
                1080,
                1620,
                2190,
                3285,
                4928,
            ],
            "times_caught": [
                24,
                168,
                336,
                720,
                1000,
                2160,
                3240,
                4380,
                6570,
                9856,
            ],
            "tanks_owned": [1, 3, 5, 10],
            "times_gambled": [
                5,
                10,
                50,
                100,
                500,
                1000,
                5000,
                10000,
                50000,
                500000,
            ],
            "money_gained": [
                1000,
                10000,
                50000,
                100000,
                250000,
                500000,
                1000000,
                1500000,
                2000000,
                5000000,
            ],
        }

        # Database variables
        async with vbu.Database() as db:
            user_achievement_milestone_data = await db(
                """SELECT * FROM user_achievements_milestones WHERE user_id = $1""",
                ctx.author.id,
            )
            user_achievement_data = await db(
                """SELECT * FROM user_achievements WHERE user_id = $1""",
                ctx.author.id,
            )
            tank_data = await db(
                """SELECT tank FROM user_tank_inventory WHERE user_id = $1""",
                ctx.author.id,
            )
            if not user_achievement_data:
                user_achievement_data = await db(
                    """INSERT INTO user_achievements (user_id) VALUES ($1) RETURNING *""",
                    ctx.author.id,
                )
            if not user_achievement_milestone_data:
                user_achievement_milestone_data = await db(
                    """INSERT INTO user_achievements_milestones (user_id) VALUES ($1) RETURNING *""",
                    ctx.author.id,
                )

        # Getting the users data into a dictionary for the embed and ease of access
        user_achievement_data_dict = {}
        for (
            achievement_type_database,
            achievement_amount_database,
        ) in user_achievement_data[0].items():
            if achievement_type_database != "user_id":
                user_achievement_data_dict[
                    achievement_type_database
                ] = achievement_amount_database

        # Getting the users amount of tanks and adding that to the user data dictionary
        tanks = 0
        if not tank_data:
            tanks = 0
        else:
            for tank in tank_data[0]["tank"]:
                if tank is True:
                    tanks += 1
        user_achievement_data_dict["tanks_owned"] = tanks

        # Setting claimable to non as default
        achievements_that_are_claimable = {}
        are_there_any_claimable_achievements_check = False

        # Creating the embed
        embed = discord.Embed(
            title=f"**{ctx.author.display_name}**'s achievements"
        )

        # Set Variables for milestones, default to nonclaimable, and default stars to nothing
        for (
            achievement,
            user_achievement_value,
        ) in user_achievement_data_dict.items():
            milestone = f"{achievement}_milestone"
            is_achievement_claimable = "nonclaimable"
            list_of_stars_per_achievement = []

            # Checks what type of star to add
            for milestone_value in milestones_dict_of_achievements[
                achievement
            ]:
                if (
                    user_achievement_milestone_data[0][f"{milestone}_done"]
                    is True
                ):
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star"]
                    )
                elif (
                    milestone_value
                    < user_achievement_milestone_data[0][milestone]
                ):
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star"]
                    )
                elif milestone_value <= user_achievement_value:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star_new"]
                    )
                else:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star_no"]
                    )

            # Grammar stuff and the number of stars said
            next_unclaimable_star = 0
            for single_star_per_star_list in list_of_stars_per_achievement:
                if single_star_per_star_list != EMOJIS["achievement_star"]:
                    next_unclaimable_star += 1
                    break
                next_unclaimable_star += 1
            st_nd_rd_th_grammar = "th"  # stundurth
            if next_unclaimable_star == 1:
                st_nd_rd_th_grammar = "st"
            elif next_unclaimable_star == 2:
                st_nd_rd_th_grammar = "nd"
            elif next_unclaimable_star == 3:
                st_nd_rd_th_grammar = "rd"

            # Sets the milestonme to be claimable if it is
            if (
                user_achievement_value
                >= user_achievement_milestone_data[0][milestone]
                and user_achievement_milestone_data[0][f"{milestone}_done"]
                is False
            ):
                if are_there_any_claimable_achievements_check is False:
                    are_there_any_claimable_achievements_check = True
                achievements_that_are_claimable[
                    achievement
                ] = milestones_dict_of_achievements[achievement].index(
                    user_achievement_milestone_data[0][milestone]
                )
                is_achievement_claimable = "claimable"
            if user_achievement_milestone_data[0][f"{milestone}_done"] is True:
                value_data = "All achievements have been claimed!"
                name_data = ""
            else:
                value_data = ""
                value_data = f"{((user_achievement_value / user_achievement_milestone_data[0][milestone]) * 100):.0f}% of **{next_unclaimable_star}**{st_nd_rd_th_grammar} star"
                name_data = f"{user_achievement_value:,}/{user_achievement_milestone_data[0][milestone]:,}"
            embed.add_field(
                name=f"{achievement.replace('_', ' ').title()} {name_data}",
                value=f"{value_data}\n{''.join(list_of_stars_per_achievement)} \n**{is_achievement_claimable}**",
            )

        # Adds a button to the message if there are any claimable achievements
        if are_there_any_claimable_achievements_check is True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        emoji="1\N{COMBINING ENCLOSING KEYCAP}",
                        custom_id="claim_all",
                    ),
                ),
            )
            claim_message = await ctx.send(embed=embed, components=components)
        else:

            # Doesnt add a button if theres no claimable achievements
            return await ctx.send(embed=embed)

        # Make the button check
        def button_check(payload):
            if payload.message.id != claim_message.id:
                return False
            v = payload.user.id == ctx.author.id
            if v:
                return True
            self.bot.loop.create_task(
                payload.response.send_message(
                    "You can't respond to this button.", ephemeral=True
                )
            )
            return False

        pressed = False
        while True:

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
                await chosen_button_payload.response.defer_update()
            except asyncio.TimeoutError:
                break
            finally:
                await claim_message.edit(
                    components=components.disable_components()
                )

            # Sets reward and if the button is clicked...
            amount_of_doubloons_earned = 0
            pressed = True
            for (
                achievement_button,
                user_achievement_position_button,
            ) in achievements_that_are_claimable.items():
                amount_per_achievement = user_achievement_position_button + 1
                for x in range(amount_per_achievement):
                    amount_of_doubloons_earned += x + 1

                # Update the user's achievement milestones
                if (
                    achievement_button == "tanks_owned"
                    and user_achievement_position_button >= 3
                ):
                    async with vbu.Database() as db:
                        await db(
                            """UPDATE user_achievements_milestones SET {} = TRUE WHERE user_id = $1""".format(
                                f"{achievement_button}_milestone_done"
                            ),
                            ctx.author.id,
                        )
                elif user_achievement_position_button >= 9:
                    async with vbu.Database() as db:
                        await db(
                            """UPDATE user_achievements_milestones SET {} = TRUE WHERE user_id = $1""".format(
                                f"{achievement_button}_milestone_done"
                            ),
                            ctx.author.id,
                        )
                else:
                    async with vbu.Database() as db:
                        await db(
                            """UPDATE user_achievements_milestones SET {} = $1 WHERE user_id = $2""".format(
                                f"{achievement_button}_milestone"
                            ),
                            milestones_dict_of_achievements[
                                achievement_button
                            ][user_achievement_position_button + 1],
                            ctx.author.id,
                        )

            # Give the user their reward balance
            async with vbu.Database() as db:
                await db(
                    """INSERT INTO user_balance (user_id, doubloon) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET doubloon = user_balance.doubloon + $2""",
                    ctx.author.id,
                    amount_of_doubloons_earned,
                )
            break

        if pressed is True:
            await ctx.send(
                f"Rewards claimed, you earned {amount_of_doubloons_earned} {EMOJIS['doubloon']}!"
            )

    @commands.command(aliases=["creds"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def credits(self, ctx: commands.Context):
        """
        Gives credit to the people who helped.
        """

        # Send the credits embed made at the beginning of cog
        await ctx.send(embed=CREDITS_EMBED)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def leaderboard(self, ctx: commands.Context):
        """
        Shows a global leaderboard of balances.
        """

        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

        async with ctx.typing():

            # Set up a select menu for them to choose which kind of leaderboard
            leaderboard_type = await utils.create_select_menu(
                self.bot, ctx, ["Balance", "Fish Points"], "type", "choose")

            # If they want the balance one...
            if leaderboard_type == "Balance":

                # Set up for the user's points
                user_points_unsorted = {}

                # Get everyone's balance
                async with vbu.Database() as db:
                    user_balance_rows = await db("""SELECT * FROM user_balance""")

                # For each row add their id and balance to the unsorted dict
                for user_info in user_balance_rows:
                    user_points_unsorted[user_info["user_id"]
                                         ] = user_info["balance"]

            # Else if they want fish points...
            elif leaderboard_type == "Fish Points":

                # Setup for their info
                user_info_unsorted = {}

                # Get their fish inventory and extra points
                async with vbu.Database() as db:
                    user_info_rows = await db(
                        """SELECT * FROM user_fish_inventory"""
                    )
                    user_extra_points = await db("""SELECT * FROM user_balance""")

                # For each row of fish...
                for user_info in user_info_rows:

                    # If that fish is alive...
                    if user_info["fish_alive"] is True:

                        # If that user's ID isn't in the dict already...
                        if user_info["user_id"] not in user_info_unsorted.keys():

                            # Add the user_id with a list to to the dict then add that fish to the list
                            user_info_unsorted[user_info["user_id"]] = []
                            user_info_unsorted[user_info["user_id"]].append(
                                user_info["fish"]
                            )

                        # Else just add the fish to the list
                        else:
                            user_info_unsorted[user_info["user_id"]].append(
                                user_info["fish"]
                            )

                # Setup for the rarity points
                rarity_points = {
                    "common": 1,
                    "uncommon": 3,
                    "rare": 15,
                    "epic": 75,
                    "legendary": 150,
                    "mythic": 1000,
                }

                # Setup for the unsorted dict
                user_points_unsorted = {}

                # For each user and their list of fish...
                for user, fish in user_info_unsorted.items():

                    # Set their points to 0
                    user_points = 0

                    # Find out what rarity each fish in the list is and add that many points
                    for rarity, fish_types in self.bot.fish.items():
                        for fish_type in fish:
                            if ' '.join(fish_type.split('_')) in fish_types:
                                user_points += rarity_points[rarity]

                    # for each user if its the correct user add the extra points as well
                    for user_name in user_extra_points:
                        if user_name["user_id"] == user:
                            user_points += user_name["extra_points"]

                    # Set the user equal to their points
                    user_points_unsorted[user] = user_points

            # Sort the points by the amount of points
            user_id_sorted = [
                (user, points)
                for user, points in sorted(
                    user_points_unsorted.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            ]

            # Set the output to be a list of strings
            output: list[str] = []

            # Format each person's id and points
            for user_id, points in user_id_sorted:
                output.append(f"<@{user_id}> ({points:,})")

        # Make a Paginator with 10 results per page
        menu = vbu.Paginator(
            output,
            per_page=10,
            formatter=vbu.Paginator.default_ranked_list_formatter,
        )

        # Return the embed
        return await menu.start(ctx)


def setup(bot):
    bot.add_cog(Informative(bot))
