import typing
import collections

import discord
from discord.ext import commands
import voxelbotutils as vbu

from cogs import utils


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
            print(fish['tank_fish'])
            if fish['tank_fish'] != '':
                fish_collections[fish['tank_fish']].append(
                    f"__**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**__\n"
                    f"**Alive:** {fish['fish_alive']}\n **Death Date:** {fish['death_time']}"
                )

        print(fish_collections)
        # Add a row in our embed for each tank
        for tank_row in tank_rows:
            for count, tank in enumerate(tank_row['tank']):
                if tank_row['tank_name'][count] in fish_collections.keys():
                    fish_message = [f"Type: {tank_row['tank_type'][count]}", f"**Fish:**", "\n".join(fish_collections[tank_row['tank_name'][count]])]
                else:
                    fish_message = ["No fish in tank."]
                if tank_row['tank'][count] is True:
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
            'Balance': (f'<:sand_dollar:852057443503964201>: {balance[0]["balance"]}x Sand Dollars', False),
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
            return await ctx.send(f"{user.display_name} has no fish in their bucket!")

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


def setup(bot):
    bot.add_cog(Informative(bot))
