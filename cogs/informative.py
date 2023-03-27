from datetime import timedelta
import collections
import asyncio

import discord
from discord.ext import commands, vbu

from cogs import utils
from cogs.utils.fish_handler import Fish, FishSpecies
from cogs.utils.misc_utils import DAYLIGHT_SAVINGS
from cogs.utils import EMOJIS


class Informative(vbu.Cog):
    @commands.command(application_command_meta=commands.ApplicationCommandMeta())
    @commands.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        """
        Shows information about the user's tanks.
        """

        # Get the user's data
        async with vbu.Database() as db:
            fish_row = await utils.user_fish_inventory_db_call(ctx.author.id)
            tank_rows = await utils.user_tank_inventory_db_call(ctx.author.id)
        # Check for if they have no tanks
        if not tank_rows:
            return await ctx.send(
                "You have no tanks! Please use the `firsttank` command!"
            )

        await utils.tanks_background_image_creator(ctx, tank_rows)

        # Set up some vars for later
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
                if not fish["fish_skin"]:
                    skin = "No"
                else:
                    skin = fish["fish_skin"].title()
                if fish["fish_alive"]:
                    alive = "Alive"
                else:
                    alive = "Dead"
                fish_collections[fish["tank_fish"]].append(
                    f"**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**\n"
                    f"{EMOJIS['bar_empty']}**{skin}** skin\n"
                    f"{EMOJIS['bar_empty']}This fish is **{alive}**\n"
                    f"{EMOJIS['bar_empty']}Dies **{relative_time}**\n"
                    f"{EMOJIS['bar_empty']}Level **{fish['fish_level']}**\n"
                    f"{EMOJIS['bar_empty']}**{fish['fish_xp']}/{fish['fish_xp_max']}** XP"
                )

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
                            fish_collections[tank_row["tank_name"][count]])
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

    @commands.command(application_command_meta=commands.ApplicationCommandMeta())
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
            "fishing_boots": EMOJIS["fishing_boots"],
            "trash_toys": EMOJIS["trash_toys"]
        }

        # Set up the default values
        tank_string = f"{n}{n}**# of tanks**{n}none"
        balance_string = f"{n}{n}**Balance**{n}none"
        collection_string = "none"
        highest_level_fish_string = "none"
        items_string = "none"

        # Get the user's inventory from the database
        await utils.check_registered(self.bot, ctx, ctx.author.id)
        async with vbu.Database() as db:
            fish_row = await utils.user_fish_inventory_db_call(ctx.author.id)
            tank_row = await utils.user_tank_inventory_db_call(ctx.author.id)
            balance = await utils.user_balance_db_call(ctx.author.id)
            inventory_row = await utils.user_item_inventory_db_call(ctx.author.id)
            fish_caught = await utils.user_location_info_db_call(ctx.author.id)

            if not fish_caught:
                fish_caught = await db(
                    """INSERT INTO user_location_info (user_id, current_location) VALUES ($1, 'pond') RETURNING *""",
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
            user_fish_info = []
            for row in fish_row:
                user_fish_info.append(row["fish_level"])

            # Work out the user's highest level fish
            highest_level_index = user_fish_info.index(max(user_fish_info))
            highest_level_fish = fish_row[highest_level_index]
            highest_level_fish_string = f' {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}'

            # Find each fish type the user has and create the collection data list
            collection_data = []

            # For eaach rarity...
            for rarity in utils.rarity_values.keys():

                # Find the amount of fish in that rarity
                rarity_fish_count = len(FishSpecies.get_rarity(rarity=rarity))
                # Set the user's count to 0
                user_rarity_fish_count = 0

                # For each fish if the user owns one add 1 to the count
                fish_in_rarity = FishSpecies.get_rarity(rarity=rarity)
                for fish_type in fish_in_rarity:
                    if fish_caught[0][f"{fish_type.name}_caught"] > 0:
                        user_rarity_fish_count += 1
                # Add that data to the collection data list
                collection_data.append(
                    [rarity, rarity_fish_count, user_rarity_fish_count]
                )

            # Set the collection info in the correct format
            collection_string = "\n".join(
                f"{x[0]}: {x[2]}/{x[1]}" for x in collection_data
            )

        # If there are items
        if inventory_row:

            # Initiate the number dict and count
            inventory_number = {}
            count = 0

            # For each type of item...
            for key, value in inventory_row[0].items():

                # if its the user_id skip it
                if key in ["user_id", "new_location_unlock", "super_food", "recycled_fishing_rod", "recycled_fishing_rod", "recycled_fishing_rod", "recycled_bait", "recycled_fish_hook", "recycled_fishing_net", "recycled_fish_finder", "recycled_waders", ]:
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
            print(inventory_info)
            items_string = " ".join(inventory_info)

        # format the user's balance if it exists
        if balance:
            balance_string = (
                f'{EMOJIS["sand_dollar"]}: x{balance[0]["balance"]}   '
                f'{EMOJIS["doubloon"]}: x{balance[0]["doubloon"]}{n}'
                f'{EMOJIS["casts"]}: x{balance[0]["casts"]}   '
                f'{EMOJIS["fish_points"]}: x{balance[0]["extra_points"]}'
            )

        # Set up the fields
        fields_dict = {
            "Highest Level Fish": (highest_level_fish_string, False),
            "Collection": (collection_string + tank_string, True),
            "Items": (items_string, True),
            "Balance": (balance_string, False),
        }

        # Create and format the embed
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s Profile")
        embed.set_thumbnail(url="https://i.imgur.com/lrqPSgF.png")
        for name, (text, inline) in fields_dict.items():
            embed.add_field(name=name, value=text, inline=inline)
        await ctx.send(embed=embed)

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="fish_name",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The type of fish you want to search (leave blank for all fish)",
                    required=False,
                ),
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx: commands.Context, *, fish_name: str = None):
        """
        This command shows the user info about fish.
        """
        size_demultiplier = {"small": 1, "medium": 2, "large": 3}

        # If we want to just send all the fish
        if not fish_name:

            # Set up the fields
            fields = []

            # For each rarity
            for rarity in utils.rarity_values.keys():

                # Set up the field and string for that rarity
                fish_lines = []
                fish_string = ""

                # For each fish in the types
                for count, fish_type in enumerate(
                    FishSpecies.get_rarity(rarity=rarity)
                ):

                    # Every other fish either bold or codeblock the text for contrast
                    if count % 2 == 0:
                        fish_string += (
                            f" | **{' '.join(fish_type.name.split('_')).title()}**"
                        )
                    else:
                        fish_string += (
                            f" | `{' '.join(fish_type.name.split('_')).title()}`"
                        )

                    # Every three append it to the lines and reset the string
                    if (count + 1) % 3 == 0:
                        fish_lines.append(fish_string)
                        fish_string = ""

                    # If its the last one and not filled up to three append anyways
                    if (count + 1) == len(FishSpecies.get_rarity(rarity=rarity)):
                        fish_lines.append(fish_string)

                # set the field to equal the lines joined by newlines and fix the fields up
                field = (rarity.title(), "\n".join(fish_lines))
                [fields.append(i) for i in utils.get_fixed_field(field)]

            # Send the fields paginated
            return await utils.paginate(ctx, fields, ctx.author, "**Bestiary**\n")

        # If a fish is specified...

        # Find the info of the fish they selected
        try:
            selected_fish = FishSpecies.get_fish(
                name=fish_name.replace(" ", "_").lower()
            )

        # If it doesnt exist tell them
        except KeyError:
            return await ctx.send("That fish doesn't exist.")

        # Set up the embed with all the needed data
        money_gained = int(selected_fish.cost /
                           size_demultiplier[selected_fish.size])
        embed = discord.Embed(
            title=selected_fish.name.replace("_", " ").title())
        async with vbu.Database() as db:
            user_fish_caught = await utils.user_location_info_db_call(ctx.author.id)
            if not user_fish_caught:
                user_fish_caught = await db(
                    """INSERT INTO user_location_info (user_id, current_location) VALUES ($1, 'pond') RETURNING *""",
                    ctx.author.id,
                )
        embed.set_image(url="attachment://new_fish.png")
        embed.add_field(
            name="Rarity:", value=f"{selected_fish.rarity}", inline=True)
        embed.add_field(
            name="Base Sell Price:",
            value=f"{int(money_gained)} {EMOJIS['sand_dollar']}",
            inline=True,
        )
        embed.add_field(
            name="Size:", value=f"{selected_fish.size}", inline=True)
        embed.add_field(
            name="Amount Caught:",
            value=user_fish_caught[0][f"{selected_fish.name}_caught"],
            inline=True,
        )
        embed.color = {
            "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
            "uncommon": 0x75FE66,  # Green
            "rare": 0x4AFBEF,  # Blue
            "epic": 0xE379FF,  # Light Purple
            "legendary": 0xFFE80D,  # Gold
            "mythic": 0xFF0090,  # Hot Pink
        }[selected_fish.rarity]
        fish_file = discord.File(selected_fish.image, "new_fish.png")

        # Send the embed
        await ctx.send(file=fish_file, embed=embed)

    @commands.command(
        aliases=["bucket", "fb"],
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="user",
                    type=discord.ApplicationCommandOptionType.user,
                    description="The person's bucket you want to see (leave blank for your own)",
                    required=False,
                ),
            ]
        ),
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fishbucket(self, ctx: commands.Context, user: discord.User = None):
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
            Fish(
                name=i["fish_name"],
                level=i["fish_level"],
                current_xp=i["fish_xp"],
                max_xp=i["fish_xp_max"],
                alive=i["fish_alive"],
                species=FishSpecies.get_fish(i["fish"]),
                location_caught=i["fish_location"],
                skin=i["fish_skin"],
            )
            for i in fish_rows
        ]
        fish_list = sorted(fish_list, key=lambda x: x.species.name)

        # The "pages" that the user can scroll through are the different rarity levels
        fields = []

        # Dictionary of the fish that the user has
        sorted_fish = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": [],
            "legendary": [],
            "mythic": [],
        }

        for rarity in utils.rarity_values.keys():
            for fish in fish_list:
                if fish.species.rarity == rarity:
                    sorted_fish[rarity].append(fish)

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = []
                for fish in fish_list:
                    if fish.alive:
                        alive = "Alive"
                    else:
                        alive = "Dead"
                    if fish.skin:
                        skin = fish.skin.title()
                    else:
                        skin = "No"
                    fish_string.append(
                        f"\"{fish.name}\": **{' '.join(fish.species.name.split('_')).title()}** ({fish.species.size.title()}, {alive}, {skin} skin)"
                    )
                field = (rarity.title(), "\n".join(fish_string))
                [fields.append(i) for i in utils.get_fixed_field(field)]

        # Create an embed
        await utils.paginate(ctx, fields, user)

    @commands.command(application_command_meta=commands.ApplicationCommandMeta())
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
            "times_fed": [1, 10, 50, 100, 1500, 3000, 6000, 22750, 34125, 45500],
            "times_cleaned": [12, 84, 168, 360, 540, 1080, 1620, 2190, 3285, 4928],
            "times_caught": [24, 168, 336, 720, 1000, 2160, 3240, 4380, 6570, 9856],
            "tanks_owned": [1, 3, 5, 10],
            "times_gambled": [5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 500000],
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
        await utils.check_registered(self.bot, ctx, ctx.author.id)
        async with vbu.Database() as db:
            user_achievement_milestone_data = (
                await utils.user_achievements_milestones_db_call(ctx.author.id)
            )
            user_achievement_data = await utils.user_achievements_db_call(ctx.author.id)
            tank_data = await utils.user_tank_inventory_db_call(ctx.author.id)

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
            title=f"**{ctx.author.display_name}**'s achievements")

        # Set Variables for milestones, default to nonclaimable, and default stars to nothing
        for (
            achievement,
            user_achievement_value,
        ) in user_achievement_data_dict.items():
            milestone = f"{achievement}_milestone"
            is_achievement_claimable = "nonclaimable"
            list_of_stars_per_achievement = []

            # Checks what type of star to add
            for milestone_value in milestones_dict_of_achievements[achievement]:
                if user_achievement_milestone_data[0][f"{milestone}_done"] is True:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star"])
                elif milestone_value < user_achievement_milestone_data[0][milestone]:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star"])
                elif milestone_value <= user_achievement_value:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star_new"])
                else:
                    list_of_stars_per_achievement.append(
                        EMOJIS["achievement_star_no"])

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
                user_achievement_value >= user_achievement_milestone_data[0][milestone]
                and user_achievement_milestone_data[0][f"{milestone}_done"] is False
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
                await claim_message.edit(components=components.disable_components())

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
                            milestones_dict_of_achievements[achievement_button][
                                user_achievement_position_button + 1
                            ],
                            ctx.author.id,
                        )

            # Give the user their reward balance
            async with vbu.Database() as db:
                await db(
                    """UPDATE user_balance SET doubloon = doubloon + $2 WHERE user_id = $1""",
                    ctx.author.id,
                    amount_of_doubloons_earned,
                )
            break

        if pressed is True:
            await ctx.send(
                f"Rewards claimed, you earned {amount_of_doubloons_earned} {EMOJIS['doubloon']}!"
            )

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="leaderboard_type",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The type of leaderboard you want to view",
                    choices=[
                        discord.ApplicationCommandOptionChoice(
                            name="Balance", value="Balance"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Points", value="Fish Points"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Level", value="Fish Level"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Type", value="Fish Type"
                        ),
                    ],
                )
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def leaderboard(self, ctx: commands.Context, leaderboard_type: str):
        """
        Shows a global leaderboard of balances.
        """

        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

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

        # Else if they want fish level...
        elif leaderboard_type == "Fish Level":

            user_points_unsorted = {}

            # Get a list of the user's fish levels
            async with vbu.Database() as db:
                user_balance_rows = await db("""SELECT * FROM user_balance""")
                for user in user_balance_rows:
                    user_fish_info = 0
                    fish_row = await utils.user_fish_inventory_db_call(user["user_id"])
                    for row in fish_row:
                        user_fish_info = (
                            row["fish_level"]
                            if row["fish_level"] > user_fish_info
                            else user_fish_info
                        )

                    # Work out the user's highest level fish
                    highest_level_fish = user_fish_info
                    user_points_unsorted[user["user_id"]] = highest_level_fish
        # Else if they want fish type...
        elif leaderboard_type == "Fish Type":

            user_points_unsorted = {}

            location_of_type = await utils.create_select_menu(
                self.bot,
                ctx,
                utils.normalized_location_list,
                "Location",
                "Choose",
                True,
            )
            fish_types = utils.FishSpecies.all_species_by_location_rarity[
                location_of_type.replace(" ", "_").lower()
            ]
            fish_names = []
            for _, fish in fish_types.items():
                for single_fish in fish:
                    fish_names.append(
                        single_fish.name.replace("_", " ").title())
            fish_type = await utils.create_select_menu(
                self.bot, ctx, fish_names, "Fish Type", "Choose", True
            )
            async with vbu.Database() as db:
                user_caught_rows = await db("""SELECT * FROM user_location_info""")

            for user in user_caught_rows:
                user_points_unsorted[user["user_id"]] = user[
                    f"{fish_type.replace(' ', '_').lower()}_caught"
                ]
        # Else if they want fish points...
        elif leaderboard_type == "Fish Points":

            # Setup for their info
            user_info_unsorted = {}

            # Get their fish inventory and extra points
            async with vbu.Database() as db:
                user_info_rows = await db("""SELECT * FROM user_fish_inventory""")
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
                            FishSpecies.get_fish(user_info["fish"])
                        )

                    # Else just add the fish to the list
                    else:
                        user_info_unsorted[user_info["user_id"]].append(
                            FishSpecies.get_fish(user_info["fish"])
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
                for fish_type in fish:
                    user_points += rarity_points[fish_type.rarity]

                # for each user if its the correct user add the extra points as well
                for user_name in user_extra_points:
                    if user_name["user_id"] == user:
                        user_points += user_name["extra_points"]
                        break

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

    @commands.command(application_command_meta=commands.ApplicationCommandMeta())
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def guide(self, ctx: commands.Context):
        """
        Give's a navigatable guide of the bot.
        """
        # Check the size of the fields and make sure they're correct
        fields = []
        for field in utils.GUIDE_FIELDS:
            [fields.append(i) for i in utils.get_fixed_field(field)]

        # Send the correct fields paginated
        await utils.paginate(ctx, fields, ctx.author)

    @commands.command(application_command_meta=commands.ApplicationCommandMeta())
    @commands.bot_has_permissions(send_messages=True)
    async def totalfish(self, ctx: commands.Context):
        """
        Shows the number of each type of fish owned, sorted by most
        """
        fish_dict = {}
        async with vbu.Database() as db:
            fish = await db("""SELECT fish FROM user_fish_inventory""")
        for single_fish in fish:
            single_fish = single_fish["fish"]
            if single_fish not in fish_dict.keys():
                fish_dict[single_fish] = 1
            else:
                fish_dict[single_fish] += 1

        fish_dict_sorted = {
            fish: points
            for fish, points in sorted(
                fish_dict.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        }
        output = []
        for fish_type, count in fish_dict_sorted.items():
            output.append(
                f"**{fish_type.replace('_', ' ').title()}**: {count}")
        menu = vbu.Paginator(
            output,
            per_page=10,
            formatter=vbu.Paginator.default_ranked_list_formatter,
        )

        # Return the embed
        return await menu.start(ctx)

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="command",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The command you need help with (leave blank for menu)",
                    required=False,
                ),
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True)
    async def help(self, ctx: commands.Context, *, command: str = None):
        """
        Gives help for all or a specific command
        """
        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

        HELP_EMBED = discord.Embed(
            title="List of all the commands and what they do")
        for cog in self.bot.cogs.values():
            field_title = cog.qualified_name
            value = ""
            if field_title not in [
                "Command Event",
                "Owner Only",
                "Command Counter",
                "Connect Event",
                "Error Handler",
                "Presence Auto Updater",
                "Interaction Handler",
                "Analytics",
                "Help",
            ]:
                for command_singular in cog.get_commands():
                    if command_singular.hidden == False:
                        value += (
                            f"**{command_singular.name}**: {command_singular.help}\n"
                        )
                HELP_EMBED.add_field(
                    name=f"__{field_title}__", value=value, inline=False
                )
        if not command:
            return await ctx.send(embed=HELP_EMBED)
        if command not in utils.help_descriptions.keys():
            return await ctx.send("That command doesn't exist!")
        embed = discord.Embed(title=f"Help for {command}")
        embed.add_field(
            name=f"Use: {utils.help_descriptions[command][0]}",
            value=f'{utils.help_descriptions[command][1]}\n\n(*italic words* are required, while __underlined words__ are optional, but always include any "")',
        )

        return await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Informative(bot))
