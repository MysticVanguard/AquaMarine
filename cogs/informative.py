import typing
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


CREDITS_EMBED = discord.Embed(
    title="Credits to all the people who have helped make this bot what it is!")
CREDITS_EMBED.add_field(
    name="The lovely coders who helped me with creating the bot, and who have taught me so much!",
    value="""
        [**Hero#2313**](https://github.com/iHeroGH): Creator of StalkerBot
        [**Kae#0004**](https://voxelfox.co.uk/): Creator of MarriageBot and so many others
        [**slippery schlöpp#6969**](https://github.com/schlopp): Creator of pp bot
    """,
    inline=False
)
CREDITS_EMBED.add_field(
    name="Credits to the wonderful Peppoco (peppoco#6867), who made these lovely emotes!",
    value="<:AquaBonk:877722771935883265><:AquaPensive:877939116266909756><:AquaFish:877939115948134442><:AquaScared:877939115943936074><:AquaShrug:877939116480802896><:AquaSmile:877939115994255383><:AquaUnamused:877939116132696085><:AquaLove:878248091201982524><:AquaCool:878248090895802438><:AquaBlep:878248090400870401>(https://peppoco.carrd.co/#)",
    inline=False
)
CREDITS_EMBED.add_field(
    name="Credits to all the people who have helped me test the bot!",
    value="""
        Aria, Astro, Dessy, Finn, George,
        Jack, Kae, Nafezra, Quig Quonk,
        Schlöpp, Toby, Victor, Ween
    """,
    inline=False
)


class Informative(vbu.Cog):

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        """
        Shows information about the user's tanks.
        """

        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
        tank_types = {
            'Fish Bowl': 'fishbowl',
            'Small Tank': 'Small_Tank_2D',
            'Medium Tank': 'Medium_Tank_2D'
        }
        position_glass = {
            'Fish Bowl': [
                (39, 16),
                (147, 16),
                (251, 16),
                (39, 64),
                (147, 64),
                (251, 64),
                (95, 117),
                (197, 117),
                (95, 154),
                (197, 154)
            ],
            'Small Tank': [
                (35, 4),
                (140, 4),
                (245, 4),
                (35, 52),
                (140, 52),
                (245, 52),
                (89, 105),
                (190, 105),
                (89, 144),
                (190, 144)
            ],
            'Medium Tank': [
                (24, 4),
                (129, 4),
                (234, 4),
                (24, 52),
                (129, 52),
                (234, 52),
                (77, 105),
                (178, 105),
                (77, 144),
                (178, 144)
            ]
        }
        position_theme = {
            'Fish Bowl': [
                (39, 16),
                (147, 16),
                (251, 16),
                (39, 64),
                (147, 64),
                (251, 64),
                (95, 117),
                (197, 117),
                (95, 154),
                (197, 154)
            ],
            'Small Tank': [
                (36, 7),
                (141, 7),
                (246, 7),
                (36, 55),
                (141, 55),
                (246, 55),
                (90, 108),
                (191, 108),
                (90, 147),
                (191, 147)
            ],
            'Medium Tank': [
                (25, 7),
                (130, 7),
                (235, 7),
                (25, 55),
                (130, 55),
                (235, 55),
                (78, 108),
                (179, 108),
                (78, 147),
                (179, 147)
            ]
        }
        id = ''.join(random.choice(string.ascii_uppercase + string.digits)
                     for _ in range(10))
        file_name = f"{file_prefix}/background/Room Walls/Tanks_Wall/User Walls/{id}user_tank_room.png"
        # Get the user's data
        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)

        background = Image.open(
            f"{file_prefix}/background/Room Walls/Tank_Wall.png").convert("RGBA")
        new_background = background.copy()
        for slot, tank in enumerate(tank_rows[0]['tank_type']):
            if tank == '':
                continue
            start = ''
            theme_raise = 0
            if (tank == 'Medium Tank' or tank == 'Small Tank') and slot in [10, 11]:
                start = 'Under_'
                theme_raise = 2
            tank_type = tank_types[tank]
            x_and_y_glass = position_glass[tank][slot]
            x_and_y_theme = position_theme[tank][slot]
            tank_theme = tank_rows[0]['tank_theme'][slot].replace(' ', '_')
            glass = Image.open(
                f"{file_prefix}/background/Room Walls/Tanks_Wall/{start}Glass_{tank_type}.png"
            ).convert("RGBA")
            theme = Image.open(
                f"{file_prefix}/background/Room Walls/Tanks_Wall/{tank_theme}_{tank_type}.png"
            ).convert("RGBA")
            print(
                f"{file_prefix}/background/Room Walls/Tanks_Wall/{tank_theme}_{tank_type}.png")
            new_background.paste(
                theme, (x_and_y_theme[0], x_and_y_theme[1]), theme)
            new_background.paste(
                glass, (x_and_y_glass[0], x_and_y_glass[1] - theme_raise), glass)

        new_background.save(file_name, format="PNG")

        await ctx.send(file=discord.File(file_name))

        # Set up some vars for later
        embed = discord.Embed()
        fish_collections = collections.defaultdict(list)
        # Get the user's fish
        for fish in fish_row:
            if fish['tank_fish'] != '':
                relative_time = discord.utils.format_dt(
                    fish['death_time'] - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                fish_collections[fish['tank_fish']].append(
                    f"**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**\n"
                    f"<:__:886381017051586580>Alive: **{fish['fish_alive']}**\n"
                    f"<:__:886381017051586580>Death Date: **{relative_time}**\n"
                    f"<:__:886381017051586580>Level: **{fish['fish_level']}**\n"
                    f"<:__:886381017051586580>XP: **{fish['fish_xp']}/{fish['fish_xp_max']}**"
                )

        if not tank_rows:
            return await ctx.send("You have no tanks!")
        # Add a row in our embed for each tank

        field = []
        n = '\n'
        for tank_row in tank_rows:
            for count in range(len(tank_row['tank'])):
                if tank_row['tank_name'][count] in fish_collections.keys():
                    fish_message = ["\n".join(
                        fish_collections[tank_row['tank_name'][count]])]
                else:
                    fish_message = [
                        "No fish in tank."]
                if tank_row['tank'][count] is True:
                    if not fish_message:
                        fish_message = [
                            "No fish in tank."]
                    field.append(
                        (f"{tank_row['tank_name'][count]} (Tank Type: {tank_row['tank_type'][count]})", "\n".join(fish_message)))
        fields = []
        for field_single in field:
            [fields.append(i) for i in utils.get_fixed_field(field_single)]
        await utils.paginate(ctx, fields, ctx.author, f"{ctx.author.display_name}'s tanks")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def profile(self, ctx: commands.Context):
        """
        Shows the user's profile.
        """
        n = "\n"
        t = "\t"
        items = {
            "cfb": "<:common_fish_bag:877646166983053383>",
            "ufb": "<:uncommon_fish_bag:877646167146651768>",
            "rfb": "<:rare_fish_bag:877646167121489930>",
            "ifb": "<:inverted_fish_bag:912057608863637545>",
            "hlfb": "<:high_level_fish_bag:912057609496985690>",
            "flakes": "<:fish_flakes:877646167188602880>",
            "pellets": "<:fish_pellets:911465714412552212>",
            "wafers": "<:fish_wafers:911465714395799574>",
            "revival": "<:revival:878297091158474793>",
            "feeding_potions": "<:feeding_potion:911465714379018261>",
            "experience_potions": "<:experience_potion:911465714412568616>",
            "mutation_potions": "<:mutation_potion:911465714420949072>",

        }
        fields_dict = {}

        # Get the user's inventory from the database
        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            balance = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            inventory_row = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # Work out the information to be displayed in the embed
        if not fish_row:
            fields_dict['Collection'] = ("none", True)
            fields_dict['Highest Level Fish'] = ("none", False)
        else:
            # Get a list of the user's fish types and levels
            user_fish = []
            user_fish_info = []
            for row in fish_row:
                user_fish.append(row['fish'])
                user_fish_info.append(row['fish_level'])

            # Work out the user's highest level fish
            highest_level_index = user_fish_info.index(max(user_fish_info))
            highest_level_fish = fish_row[highest_level_index]

            # Work out how many fish from each rarity level the user has
            collection_data = []
            user_fish_types = set([i['fish'] for i in fish_row])
            if not tank_row:
                tank_string = f"{n}{n}**# of tanks**{n}none"
            else:
                # Get the number of tanks that the user has
                number_of_tanks = 0
                if tank_row:
                    number_of_tanks = tank_row[0]['tank'].count(True)
                tank_string = f"{n}{n}**# of tanks**{n}{number_of_tanks}"
            for rarity, fish in self.bot.fish.items():
                # The number of fish in a given rarity
                fields_dict['Highest Level Fish'] = (
                    f' {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}', False)
                rarity_fish_count = len(fish)
                user_rarity_fish_count = 0  # The number in that rarity that the user has
                for info in fish.values():
                    if info['raw_name'] in user_fish_types:
                        user_rarity_fish_count += 1
                collection_data.append(
                    [rarity, rarity_fish_count, user_rarity_fish_count])
                collection_info = [
                    f"{x[0]}: {x[2]}/{x[1]}" for x in collection_data]
                fields_dict['Collection'] = (
                    ("\n".join(collection_info)+tank_string), True)
        if not inventory_row:
            fields_dict['Items'] = ("none", True)
        else:
            # Get the number of items that the user has from their inventory
            inventory_number = {}
            count = 0
            for key, value in inventory_row[0].items():
                print(key, value)
                if key == "user_id":
                    continue
                if (count % 3) == 0 and count != 0:
                    inventory_number[("\n"+(items[key]))] = (str(value))
                else:
                    inventory_number[items[key]] = value
                count += 1
            if not balance:
                balance_string = f"{n}{n}**Balance**{n}none"
            else:
                balance_string = f'{n}{n}**Balance**{n}<:sand_dollar:877646167494762586>: x{balance[0]["balance"]}   <:doubloon:878297091057807400>: x{balance[0]["doubloon"]}{n}<:Casts:911465713938612235>: x{balance[0]["casts"]}   <:fish_points:911468089420427324>: x{balance[0]["extra_points"]}'
            inventory_info = [
                f"{inv_key}: x{inv_value}" for inv_key, inv_value in inventory_number.items()]

            fields_dict['Items'] = (
                (' '.join(inventory_info)+balance_string), True)

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

        # See if we want to list all of the fish
        if not fish_name:
            fields = []
            embed = discord.Embed(title="All Fish")
            for rarity, fish_types in self.bot.fish.items():
                fish_string = [
                    f"**{' '.join(fish_type.split('_')).title()}**" for fish_type, fish_info in fish_types.items()]
                fields.append((rarity.title(), "\n".join(fish_string)))
            return await utils.paginate(ctx, fields, ctx.author, "**Bestiary**\n")

        # Find the fish they asked for
        inverted = False
        if 'inverted' in fish_name.lower():
            fish_name = fish_name.replace('inverted ', '')
            inverted = True

        selected_fish = None
        for rarity, fish_types in self.bot.fish.items():
            for _, fish_info in fish_types.items():
                if fish_info["name"] == str(fish_name.title()):
                    selected_fish = fish_info
                    break
            if selected_fish:
                break
        else:
            return await ctx.send("That fish doesn't exist.")

        # Make and send an embed
        if inverted is True:
            utils.make_inverted(selected_fish)

        embed = discord.Embed(title=selected_fish["name"])
        embed.set_image(url="attachment://new_fish.png")
        embed.add_field(
            name='Rarity:', value=f"{selected_fish['rarity']}", inline=False)
        embed.add_field(name='Base Sell Price:',
                        value=f"{int(selected_fish['cost'])} <:sand_dollar:877646167494762586>", inline=False)
        embed.add_field(
            name='Size:', value=f"{selected_fish['size']}", inline=False)
        embed.color = {
            "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
            "uncommon": 0x75FE66,  # Green
            "rare": 0x4AFBEF,  # Blue
            "epic": 0xE379FF,  # Light Purple
            "legendary": 0xFFE80D,  # Gold
            "mythic": 0xFF0090,  # Hot Pink
        }[selected_fish['rarity']]
        fish_file = discord.File(selected_fish["image"], "new_fish.png")
        await ctx.send(file=fish_file, embed=embed)

    @commands.command(aliases=["bucket", "fb"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True)
    async def fishbucket(self, ctx: commands.Context, user: discord.User = None):
        """
        Show a user's fishbucket.
        """

        # Default the user to the author of the command
        user = user or ctx.author

        # Get the fish information
        async with vbu.Database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish=''""", user.id)
        if not fish_rows:
            if user == ctx.author:
                return await ctx.send("You have no fish in your bucket!")
            return await ctx.send(f"**{user.display_name}** has no fish in their bucket!")

        fish_list = [(i['fish_name'], i['fish'], i['fish_alive'])
                     for i in fish_rows]  # List of tuples (Fish Name, Fish Type)
        fish_list = sorted(fish_list, key=lambda x: x[1])

        fields = []  # The "pages" that the user can scroll through are the different rarity levels

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
        for rarity, fish_types in self.bot.fish.items():  # For each rarity level
            for _, fish_detail in fish_types.items():  # For each fish in that level
                raw_name = fish_detail["raw_name"]
                for user_fish_name, user_fish, alive in fish_list:
                    # If the fish in the user's list matches the name of a fish in the rarity catgeory
                    if raw_name == utils.get_normal_name(user_fish):
                        # Append to the dictionary
                        sorted_fish[rarity].append(
                            (user_fish_name, user_fish, fish_detail['size'], alive))

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [
                    f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}** (Size: {fish_size.title()}, Alive: {alive})" for fish_name, fish_type, fish_size, alive in fish_list]
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
            'times_entertained': [96, 672, 1344, 2880, 8640, 17280, 25920, 35040, 52512, 70080],
            'times_fed': [1, 10, 50, 100, 1500, 3000, 6000, 22750, 34125, 45500],
            'times_cleaned': [12, 84, 168, 360, 540, 1080, 1620, 2190, 3285, 4928],
            'times_caught': [24, 168, 336, 720, 1000, 2160, 3240, 4380, 6570, 9856],
            'tanks_owned': [1, 3, 5, 10],
            'times_gambled': [5, 10, 50, 100, 500, 1000, 5000, 10000, 50000, 500000],
            'money_gained': [1000, 10000, 50000, 100000, 250000, 500000, 1000000, 1500000, 2000000, 5000000],
        }

        # Database variables
        async with vbu.Database() as db:
            user_achievement_milestone_data = await db("""SELECT * FROM user_achievements_milestones WHERE user_id = $1""", ctx.author.id)
            user_achievement_data = await db("""SELECT * FROM user_achievements WHERE user_id = $1""", ctx.author.id)
            tank_data = await db("""SELECT tank FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            if not user_achievement_data:
                user_achievement_data = await db("""INSERT INTO user_achievements (user_id) VALUES ($1) RETURNING *""", ctx.author.id)
            if not user_achievement_milestone_data:
                user_achievement_milestone_data = await db("""INSERT INTO user_achievements_milestones (user_id) VALUES ($1) RETURNING *""", ctx.author.id)

        # Getting the users data into a dictionary for the embed and ease of access
        user_achievement_data_dict = {}
        for achievement_type_database, achievement_amount_database in user_achievement_data[0].items():
            if achievement_type_database != "user_id":
                user_achievement_data_dict[achievement_type_database] = achievement_amount_database

        # Getting the users amount of tanks and adding that to the user data dictionary
        tanks = 0
        if not tank_data:
            tanks = 0
        else:
            for tank in tank_data[0]['tank']:
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
        for achievement, user_achievement_value in user_achievement_data_dict.items():
            milestone = f"{achievement}_milestone"
            is_achievement_claimable = "nonclaimable"
            list_of_stars_per_achievement = []

            # Checks what type of star to add
            for milestone_value in milestones_dict_of_achievements[achievement]:
                if user_achievement_milestone_data[0][f"{milestone}_done"] is True:
                    list_of_stars_per_achievement.append(
                        "<:achievement_star:877646167087906816>")
                elif milestone_value < user_achievement_milestone_data[0][milestone]:
                    list_of_stars_per_achievement.append(
                        "<:achievement_star:877646167087906816>")
                elif milestone_value <= user_achievement_value:
                    list_of_stars_per_achievement.append(
                        "<:achievement_star_new:877737712046702592>")
                else:
                    list_of_stars_per_achievement.append(
                        "<:achievement_star_no:877646167222141008>")

            # Grammar stuff and the number of stars said
            next_unclaimable_star = 0
            for single_star_per_star_list in list_of_stars_per_achievement:
                if single_star_per_star_list != "<:achievement_star:877646167087906816>":
                    next_unclaimable_star += 1
                    break
                next_unclaimable_star += 1
            st_nd_rd_th_grammar = 'th'  # stundurth
            if next_unclaimable_star == 1:
                st_nd_rd_th_grammar = 'st'
            elif next_unclaimable_star == 2:
                st_nd_rd_th_grammar = 'nd'
            elif next_unclaimable_star == 3:
                st_nd_rd_th_grammar = 'rd'

            # Sets the milestonme to be claimable if it is
            if user_achievement_value >= user_achievement_milestone_data[0][milestone] and user_achievement_milestone_data[0][f'{milestone}_done'] is False:
                if are_there_any_claimable_achievements_check is False:
                    are_there_any_claimable_achievements_check = True
                achievements_that_are_claimable[achievement] = milestones_dict_of_achievements[achievement].index(
                    user_achievement_milestone_data[0][milestone])
                is_achievement_claimable = "claimable"
            if user_achievement_milestone_data[0][f'{milestone}_done'] is True:
                value_data = 'All achievements have been claimed!'
                name_data = ''
            else:
                value_data = ''
                value_data = f"{((user_achievement_value / user_achievement_milestone_data[0][milestone]) * 100):.0f}% of **{next_unclaimable_star}**{st_nd_rd_th_grammar} star"
                name_data = f"{user_achievement_value:,}/{user_achievement_milestone_data[0][milestone]:,}"
            embed.add_field(name=f"{achievement.replace('_', ' ').title()} {name_data}",
                            value=f"{value_data}\n{''.join(list_of_stars_per_achievement)} \n**{is_achievement_claimable}**")

        # Adds a button to the message if there are any claimable achievements
        if are_there_any_claimable_achievements_check is True:
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        emoji="1\N{COMBINING ENCLOSING KEYCAP}", custom_id="claim_all"),
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
            self.bot.loop.create_task(payload.response.send_message(
                "You can't respond to this button.", ephemeral=True))
            return False

        pressed = False
        while True:

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for('component_interaction', timeout=60.0, check=button_check)
                await chosen_button_payload.response.defer_update()
            except asyncio.TimeoutError:
                break
            finally:
                await claim_message.edit(components=components.disable_components())

            # Sets reward and if the button is clicked...
            amount_of_doubloons_earned = 0
            pressed = True
            for achievement_button, user_achievement_position_button in achievements_that_are_claimable.items():
                amount_per_achievement = user_achievement_position_button + 1
                for x in range(amount_per_achievement):
                    amount_of_doubloons_earned += x + 1

                # Update the user's achievement milestones
                if achievement_button == 'tanks_owned' and user_achievement_position_button >= 3:
                    async with vbu.Database() as db:
                        await db("""UPDATE user_achievements_milestones SET {0} = TRUE WHERE user_id = $1""".format(f"{achievement_button}_milestone_done"), ctx.author.id)
                elif user_achievement_position_button >= 9:
                    async with vbu.Database() as db:
                        await db("""UPDATE user_achievements_milestones SET {0} = TRUE WHERE user_id = $1""".format(f"{achievement_button}_milestone_done"), ctx.author.id)
                else:
                    async with vbu.Database() as db:
                        await db("""UPDATE user_achievements_milestones SET {0} = $1 WHERE user_id = $2""".format(f"{achievement_button}_milestone"), milestones_dict_of_achievements[achievement_button][user_achievement_position_button + 1], ctx.author.id)

            # Give the user their reward balance
            async with vbu.Database() as db:
                await db(
                    """INSERT INTO user_balance (user_id, doubloon) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET doubloon = user_balance.doubloon + $2""",
                    ctx.author.id, amount_of_doubloons_earned)
            break

        if pressed is True:
            await ctx.send(f"Rewards claimed, you earned {amount_of_doubloons_earned} <:doubloon:878297091057807400>!")

    @commands.command(aliases=["creds"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def credits(self, ctx: commands.Context):
        """
        Gives credit to the people who helped.
        """

        await ctx.send(embed=CREDITS_EMBED)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def leaderboard(self, ctx: commands.Context):
        """
        Shows a global leaderboard of balances.
        """

        async with ctx.typing():
            user_info_unsorted = {}
            user_info_sorted = {}
            async with vbu.Database() as db:
                user_info_rows = await db("""SELECT * FROM user_fish_inventory""")
                user_extra_points = await db("""SELECT * FROM user_balance""")
            for user_info in user_info_rows:
                if user_info['fish_alive'] is True:
                    if user_info['user_id'] not in user_info_unsorted.keys():
                        user_info_unsorted[user_info['user_id']] = []
                        user_info_unsorted[user_info['user_id']].append(
                            user_info['fish'])
                    else:
                        user_info_unsorted[user_info['user_id']].append(
                            user_info['fish'])
            rarity_points = {
                "common": 1,
                "uncommon": 3,
                "rare": 15,
                "epic": 75,
                "legendary": 150,
                "mythic": 1000
            }

            user_points_unsorted = {}
            for user, fish in user_info_unsorted.items():
                user_points = 0
                for rarity, fish_types in self.bot.fish.items():
                    for fish_type in fish:
                        if fish_type in fish_types:
                            user_points += rarity_points[rarity]
                for user_name in user_extra_points:
                    if user_name["user_id"] == user:
                        user_points += user_name['extra_points']
                user_points_unsorted[user] = user_points
            user_id_sorted = [(user, points) for user, points in sorted(
                user_points_unsorted.items(), key=lambda item: item[1], reverse=True)]
            output: typing.List[str] = []
            for user_id, points in user_id_sorted:
                output.append(f"<@{user_id}> ({points:,})")
        menu = vbu.Paginator(
            output, per_page=10, formatter=vbu.Paginator.default_ranked_list_formatter)
        return await menu.start(ctx)


def setup(bot):
    bot.add_cog(Informative(bot))
