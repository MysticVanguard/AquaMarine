from datetime import timedelta
from itertools import filterfalse
import re
import typing
import collections
import asyncio

import discord
from discord.ext import commands
import voxelbotutils as vbu
from voxelbotutils.cogs.utils.context_embed import Embed

from cogs import utils

CREDITS_EMBED = discord.Embed(title="Credits to all the people who have helped make this bot what it is!")
CREDITS_EMBED.add_field(
    name="The lovely coders who helped me with creating the bot, and who have taught me so much!",
    value="""**Hero#2313**: Creator of stalkerbot
    (https://github.com/iHeroGH)
    **Kae#0004**: Creator of marriagebot and so many others
    (https://github.com/4Kaylum, https://voxelfox.co.uk/)
    **slippery schlöpp#6969**: Creater of ppbot
    (https://github.com/schlopp)
    """,
    inline=False
)
CREDITS_EMBED.add_field(
    name="Credits to the wonderful Peppoco (peppoco#6867), who made these lovely emotes!",
    value="<:AquaBonk:877722771935883265><:AquaPensive:877939116266909756><:AquaFish:877939115948134442><:AquaScared:877939115943936074><:AquaShrug:877939116480802896><:AquaSmile:877939115994255383><:AquaUnamused:877939116132696085>(https://peppoco.carrd.co/#)",
    inline=False
)
CREDITS_EMBED.add_field(
    name="Credits to all the people who have helped me test the bot!",
    value="""Aria, Astro, Dessy, Finn, George,
    Jack, Kae, Nafezra, Quig Quonk,
    Schlöpp, Toby, Tor
    """,
    inline=False
)



class Informative(vbu.Cog):

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        """
        Shows information about the users tanks.
        """

        # Get the user's data
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)

        # Set up some vars for later
        embed = discord.Embed()
        fish_collections = collections.defaultdict(list)
        # Get the user's fish
        for fish in fish_row:
            if fish['tank_fish'] != '':
                fish_collections[fish['tank_fish']].append(
                    f"__**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**__\n"
                    f"**Alive:** {fish['fish_alive']}\n **Death Date:** {vbu.TimeFormatter(fish['death_time'] - timedelta(hours=4)).relative_time}"
                )

        if not tank_rows:
            return await ctx.send("You have no tanks!")
        # Add a row in our embed for each tank
        for tank_row in tank_rows:
            for count, tank in enumerate(tank_row['tank']):
                if tank_row['tank_name'][count] in fish_collections.keys():
                    fish_message = [f"Type: {tank_row['tank_type'][count]}", f"**Fish:**", "\n".join(fish_collections[tank_row['tank_name'][count]])]
                else:
                    fish_message = ["No fish in tank."]
                if tank_row['tank'][count] is True:
                    if not fish_message:
                        fish_message = ["No fish in tank."]

                    embed.add_field(
                        name=tank_row['tank_name'][count],
                        value=
                        "\n".join(fish_message)

                    )

        # And send
        await ctx.send(embed=embed)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def profile(self, ctx: commands.Context):
        """
        Shows the users profile.
        """

        items = [
            "<:common_fish_bag:851974760510521375>",
            "<:uncommon_fish_bag:851974792864595988>",
            "<:rare_fish_bag:851974785088618516>",
            "<:epic_fish_bag:851974770467930118>",
            "<:legendary_fish_bag:851974777567838258>",
            "<:fish_flakes:852053373111894017>",
        ]

        # Get the user's inventory from the database
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            balance = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            inventory_row = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # Get a list of the user's fish types and levels
        user_fish = []
        user_fish_info = []
        for row in fish_row:
            user_fish.append(row['fish'])
            user_fish_info.append(row['fish_level'])

        # Work out the user's highest level fish
        highest_level_index = user_fish_info.index(max(user_fish_info))
        highest_level_fish = fish_row[highest_level_index]

        # Get the emoji for the user's highest level fish, as well as how many of each given
        # fish they have
        fish_number = {}
        highest_level_fish_emoji = ""
        for rarity, fish in utils.EMOJI_RARITIES.items():

            # Get the emoji for the highest level fish that the user has
            for name, emoji in fish.items():
                if highest_level_fish['fish'] == name:
                    highest_level_fish_emoji = emoji
                    break

            # Get the number of fish that the user has by emoji
            for fish_owned in set(user_fish):
                emoji = fish[fish_owned]
                fish_number[emoji] = user_fish.count(fish_owned)

        # Format a string for the embed
        fish_info = [f"{fish_key}: {fish_value}x" for fish_key, fish_value in fish_number.items()]

        # Work out how many fish from each rarity level the user has
        collection_data = []
        user_fish_types = set([i['fish'] for i in fish_row])
        for rarity, fish in self.bot.fish.items():
            rarity_fish_count = len(fish)  # The number of fish in a given rarity
            user_rarity_fish_count = 0  # The number in that rarity that the user has
            for info in fish.values():
                if info['raw_name'] in user_fish_types:
                    user_rarity_fish_count += 1
            collection_data.append([rarity, rarity_fish_count, user_rarity_fish_count])

        # Get the number of items that the user has from their inventory
        inventory_number = {i: 0 for i in items}
        for row in inventory_row:
            for key, value in row.items():
                if key == "user_id":
                    continue
                inventory_number[key] = value

        # Get the number of tanks that the user has
        number_of_tanks = 0
        if tank_row:
            number_of_tanks = tank_row[0]['tank'].count(True)

        # Format some strings for our embed
        inventory_info = [f"{inv_key}: {inv_value}x" for inv_key, inv_value in inventory_number.items()]
        collection_info = [f"{x[0]}: {x[2]}/{x[1]}" for x in collection_data]
        fields_dict = {
            'Collection': ("\n".join(collection_info), False),
            'Balance': (f'<:sand_dollar:877646167494762586>: {balance[0]["balance"]}x', False),
            '# of Tanks': (number_of_tanks, False),
            'Highest Level Fish': (f'{highest_level_fish_emoji} {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}', False),
            'Achievements': ("Soon To Be Added.", True),
            'Owned Fish': (' '.join(fish_info), True),
            'Items': (' '.join(inventory_info), True),
        }

        # Work out the information to be displayed in the embed
        if not collection_info:
            fields_dict['Collection'] = ("none", False)
        if not balance:
            fields_dict['Balance'] = ("none", False)
        if not number_of_tanks:
            fields_dict['# of Tanks'] = ("none", False)
        if not highest_level_fish_emoji:
            fields_dict['Highest Level Fish'] = ("none", False)
        if not fish_info:
            fields_dict['Owned Fish'] = ("none", True)
        if not inventory_info:
            fields_dict['Items'] = ("none", True)

        # Create and format the embed
        embed = vbu.Embed(title=f"{ctx.author.display_name}'s Profile")
        embed.set_thumbnail(url="https://i.imgur.com/lrqPSgF.png")
        for name, (text, inline) in fields_dict.items():
            embed.add_field(name=name, value=text, inline=inline)
        await ctx.send(embed=embed)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx: commands.Context, *, fish_name: str = None):
        """
        This command shows you info about fish.
        """

        # See if we want to list all of the fish
        if not fish_name:
            fields = []
            embed = discord.Embed(title="All Fish")
            for rarity, fish_types in self.bot.fish.items():
                fish_string = [f"**{' '.join(fish_type.split('_')).title()}**" for fish_type, fish_info in fish_types.items()]
                fields.append((rarity.title(), "\n".join(fish_string)))
            return await utils.paginate(ctx, fields, ctx.author, "**Bestiary**\n")

        # Find the fish they asked for
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
        embed = discord.Embed(title=selected_fish["name"])
        embed.set_image(url="attachment://new_fish.png")
        embed.add_field(name='Rarity', value=f"This fish is {selected_fish['rarity']}", inline=False)
        embed.add_field(name='Cost', value=f"This fish is {selected_fish['cost']}", inline=False)
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

    @vbu.command(aliases=["bucket", "fb"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True)
    async def fishbucket(self, ctx: commands.Context, user: discord.User = None):
        """
        Show a user's fishbucket.
        """

        # Default the user to the author of the command
        user = user or ctx.author

        # Get the fish information
        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish=''""", user.id)
        if not fish_rows:
            if user == ctx.author:
                return await ctx.send("You have no fish in your bucket!")
            return await ctx.send(f"**{user.display_name}** has no fish in their bucket!")

        fish_list = [(i['fish_name'], i['fish']) for i in fish_rows]  # List of tuples (Fish Name, Fish Type)
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
                for user_fish_name, user_fish in fish_list:
                    if raw_name == utils.get_normal_name(user_fish):  # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        sorted_fish[rarity].append((user_fish_name, user_fish, fish_detail['size']))  # Append to the dictionary

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}** ({fish_size.title()})" for fish_name, fish_type, fish_size in fish_list]
                field = (rarity.title(), "\n".join(fish_string))
                [fields.append(i) for i in utils.get_fixed_field(field)]

        # Create an embed
        await utils.paginate(ctx, fields, user)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def achievements(self, ctx: commands.Context):
        # The milestones for each achievement type
        milestones = {
               'times_entertained': [5, 25, 100, 250, 500, 1000, 5000, 10000, 100000, 1000000],
                'times_fed': [5, 25, 100, 250, 500, 1000, 5000, 10000, 100000, 1000000],
                'times_cleaned': [5, 25, 100, 250, 500, 1000, 5000, 10000, 100000, 1000000],
                'times_caught': [5, 25, 100, 250, 500, 1000, 5000, 10000, 100000, 1000000],
                'tanks_owned': [1, 3, 5, 10],
                'times_gambled': [5, 25, 100, 250, 500, 1000, 5000, 10000, 100000, 1000000],
                'money_gained': [100, 250, 500, 1000, 5000, 10000, 100000, 1000000, 10000000, 100000000],
        }


        # Database variables
        async with self.bot.database() as db:
            achievement_data_milestones = await db("""SELECT * FROM user_achievements_milestones WHERE user_id = $1""", ctx.author.id)
            achievement_data = await db("""SELECT * FROM user_achievements WHERE user_id = $1""", ctx.author.id)
            tank_data = await db("""SELECT tank FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            if not achievement_data:
                achievement_data = await db("""INSERT INTO user_achievements (user_id) VALUES ($1) RETURNING *""", ctx.author.id)
            if not achievement_data_milestones:
                achievement_data_milestones = await db("""INSERT INTO user_achievements_milestones (user_id) VALUES ($1) RETURNING *""", ctx.author.id)

        # Getting the users data into a dictionary for the embed and ease of access
        data = {}
        for value_type, count in achievement_data[0].items():
            if value_type != "user_id":
                data[value_type] = count

        # Getting the users amount of tanks and adding that to the user data dictionary
        tanks = 0
        if not tank_data:
            tanks = 0
        else:
            for tank in tank_data[0]['tank']:
                if tank is True:
                    tanks += 1
        data["tanks_owned"] = tanks

        # Setting claimable to non as default

        claimable_dict = {}
        claims = False

        # Creating the embed as well as checking if the achievement is claimable
        embed = discord.Embed(title=f"**{ctx.author.display_name}**'s achievements")
        for type, value in data.items():
            milestone = f"{type}_milestone"
            claimable_nonclaimable = "nonclaimable"
            stars = []
            for data in milestones[type]:
                if data < achievement_data_milestones[0][milestone]:
                    stars.append("<:achievement_star:877646167087906816>")
                elif data <= value:
                    stars.append("<:achievement_star_new:877737712046702592>")
                else:
                    stars.append("<:achievement_star_no:877646167222141008>")
            star_number_next = 0
            st_nd_rd_th = 'th'
            for star in stars:
                if star == "<:achievement_star_no:877646167222141008>":
                    star_number_next += 1
                    break
                star_number_next += 1
            if star_number_next == 1:
                st_nd_rd_th = 'st'
            elif star_number_next == 2:
                st_nd_rd_th = 'nd'
            elif star_number_next == 3:
                st_nd_rd_th = 'rd'

            if value >= achievement_data_milestones[0][milestone]:
                if claims is False:
                    claims = True
                claimable_dict[type] = value
                claimable_nonclaimable = "claimable"
            embed.add_field(name=f"{type.replace('_', ' ').title()} {value:,}/{achievement_data_milestones[0][milestone]:,}", value=f"{(value/achievement_data_milestones[0][milestone])}% of **{star_number_next}**{st_nd_rd_th} star\n{''.join(stars)} \n**{claimable_nonclaimable}**")

        if claims is True:
            components = vbu.MessageComponents(
                vbu.ActionRow(
                    vbu.Button(custom_id="claim_all", emoji="1\N{COMBINING ENCLOSING KEYCAP}"),
                ),
            )
            claim_message = await ctx.send(embed=embed, components=components)
        else:
            return await ctx.send(embed=embed)

        # Make the button check
        def button_check(payload):
            if payload.message.id != claim_message.id:
                return False
            self.bot.loop.create_task(payload.defer_update())
            return payload.user.id == ctx.author.id

        pressed = False
        while True:

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for('component_interaction', timeout=60.0, check=button_check)
                chosen_button = chosen_button_payload.component.custom_id.lower()
            except asyncio.TimeoutError:
                await claim_message.edit(components=components.disable_components())
                break

            reward = 0
            # Update the displayed emoji
            if chosen_button == "claim_all":
                pressed = True
                for type, value in claimable_dict.items():
                    for count, data in enumerate(milestones[type]):
                        if value >= data and data >= achievement_data_milestones[0][milestone]:
                            reward += (count + 1)
                            print(reward)
                        else:
                            new_milestone = milestones[type][(count)]
                            break

                    async with self.bot.database() as db:
                        await db("""UPDATE user_achievements_milestones SET {0} = $1 WHERE user_id = $2""".format(f"{type}_milestone"), new_milestone, ctx.author.id)
                async with self.bot.database() as db:
                    await db(
                        """INSERT INTO user_balance (user_id, doubloon) VALUES ($1, $2)
                        ON CONFLICT (user_id) DO UPDATE SET doubloon = user_balance.doubloon + $2""",
                        ctx.author.id, reward)
                components.get_component(chosen_button).disable()
            break
        if pressed is True:
            await ctx.send(f"Rewards claimed, you earned {reward} doubloons!")

    @vbu.command(aliases=["creds"])
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def credits(self, ctx: commands.Context):
        """
        This command gives credit to the people who helped.
        """

        await ctx.send(embed=CREDITS_EMBED)

def setup(bot):
    bot.add_cog(Informative(bot))
