from gc import collect
import random

import re
import asyncio
import typing

import discord
from discord.ext import commands
import math

import utils

HELP_TEXT_GENERAL = """
**For a list of commands, run `a.commands`!**
Welcome to Aquamarine, your virtual fishing, fish care, and aquarium bot! 
To start off run the `a.fish` command and react to one of the options. run the `a.firsttank` command to get your first tank for free, and start your adventure owning tanks. 
To deposit a fish into a tank use `a.dep "tank name" "fish name"` (although remember, each tank has a limited capacity). 
Once a fish is in a tank you can feed them (`a.feed "fish name"`) to keep them alive and entertain them (`a.entertain "fish name"`) to give them XP. 
To feed a fish, you need to buy fish food from the shop (`a.shop` to see the shop). To buy, use the `a.buy "item" "amount(optional)"` command.
To get help on certain commands, use `a.help "command"`.
"""

class Informative(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        '''
        `a.tanks` shows information about the users tanks.
        '''
        die = '\n'
        count = 0
        async with utils.DatabaseConnection() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)
        embed = discord.Embed()
        for name in tank_row[0]['tank_name']:
            if name:
                fish_text = []
                for fish in fish_row:
                    if fish['tank_fish'] == name:
                        fish_text.append(f"**{fish['fish'].replace('_', ' ').title()}: \"{fish['fish_name']}\"**\n**LVL.** {fish['fish_level']} **Alive:** {fish['fish_alive']} **Death Date:** {fish['death_time']}")
                embed.add_field(name=name, value=f"Type: {tank_row[0]['tank_type'][count]}\n**Fish:**\n{die.join(fish_text)}")
            count += 1
        print(embed)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def profile(self, ctx: commands.Context):
        '''
        `a.profile` Shows the users profile.
        '''
        rarity_max = 0
        rarity_min = 0
        user_fish = []
        user_fish_info = []
        fish_number = {}
        count = 0
        number_of_tanks = 0
        highest_level_fish_emoji = ""
        inventory_data = []
        collection_data = []
        collection_fish = []
        items = [
            "<:common_fish_bag:851974760510521375>", 
            "<:uncommon_fish_bag:851974792864595988>", 
            "<:rare_fish_bag:851974785088618516>", 
            "<:epic_fish_bag:851974770467930118>", 
            "<:legendary_fish_bag:851974777567838258>", 
            "<:fish_flakes:852053373111894017>"
            ]
        inventory_number = {}

        async with utils.DatabaseConnection() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)
            balance = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            inventory_row = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)  
         
        for row in fish_row:
            user_fish.append(row['fish'])
            user_fish_info.append(row['fish_level'])
        highest_level_index = user_fish_info.index(max(user_fish_info))
        highest_level_fish = fish_row[highest_level_index]

        for rarity, fish in utils.EMOJI_RARITIES.items():
            for name, emoji in fish.items():
                if highest_level_fish['fish'] == name:
                    highest_level_fish_emoji = emoji
                for fish_owned in user_fish:
                    if name == fish_owned and emoji not in fish_number.keys():
                        fish_number[emoji] = user_fish.count(fish_owned)
        fish_info = [f"{fish_key}: {fish_value}x" for fish_key, fish_value in fish_number.items()]
    
        for rarity, fish in self.bot.fish.items():
            for name, info in fish.items():
                rarity_max += 1
                for fish in fish_row:
                    if info['raw_name'] == fish['fish'] and fish['fish'] not in collection_fish:
                        rarity_min += 1
                        collection_fish.append(fish['fish'])
            collection_data.append([rarity, rarity_max, rarity_min])
            rarity_min = 0
            rarity_max = 0
                    

        for info in inventory_row:
            for values in info:
                if values < 1000000:
                    inventory_data.append(values)
        if not inventory_row:
            for item in items:
                inventory_number[item] = 0
        else:
            for item in items:
                inventory_number[item] = inventory_data[count]
                count += 1
        if not tank_row:
            pass
        else:
            for tank in tank_row[0]['tank']:
                if tank:
                    number_of_tanks += 1

        inventory_info = [f"{inv_key}: {inv_value}x" for inv_key, inv_value in inventory_number.items()]
        collection_info = [f"{x[0]}: {x[2]}/{x[1]}" for x in collection_data]

        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s Profile"
        embed.set_thumbnail(url='https://imgur.com/a/7sGHrse')
        embed.add_field(name='Collection', value="\n".join(collection_info), inline=False)
        embed.add_field(name='Balance', value=f'<:sand_dollar:852057443503964201>: {balance[0]["balance"]}x Sand Dollars', inline=False)
        embed.add_field(name='# of Tanks:', value=number_of_tanks, inline=False)
        embed.add_field(name='Highest Level Fish:', value=f'{highest_level_fish_emoji} {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}', inline=False)
        embed.add_field(name="Achievements:", value= "Soon To Be Added.", inline=True)
        embed.add_field(name='Owned Fish', value=' '.join(fish_info), inline=True)
        embed.add_field(name='Items', value=' '.join(inventory_info), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx:commands.Context, fish_name: typing.Optional[str]):
        '''`a.bestiary \"fish type(optional)\"` This command shows you a list of all the fish in the bot. If a fish is specified information about that fish is shown'''
        new_fish = {}
        fields = []
        if not fish_name:
            embed = discord.Embed()
            embed.title = "All Fish"
            for rarity, fish_types in self.bot.fish.items():
                fish_string = [f"**{' '.join(fish_type.split('_')).title()}**" for fish_type, fish_info in fish_types.items()]
                fields.append((rarity.title(), "\n".join(fish_string)))

            # Create an embed
            curr_index = 1
            curr_field = fields[curr_index - 1]
            embed = self.create_bucket_embed(ctx.author, curr_field, "**Bestiary**\n")

            fish_message = await ctx.send(embed=embed)

            valid_reactions = ["◀️", "▶️", "⏹️", "🔢"]
            [await fish_message.add_reaction(reaction) for reaction in valid_reactions]  # Add the pagination reactions to the message

            def reaction_check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in valid_reactions and reaction.message == fish_message

            while True:  # Keep paginating until the user clicks stop
                try:
                    chosen_reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                    chosen_reaction = chosen_reaction.emoji
                except asyncio.TimeoutError:
                    chosen_reaction = "⏹️"
                
                index_chooser = {
                    "◀️": max(1, curr_index - 1),
                    "▶️": min(len(fields), curr_index + 1)
                }
                
                if chosen_reaction in index_chooser.keys():
                    curr_index = index_chooser[chosen_reaction]  # Keep the index in bounds
                    curr_field = fields[curr_index - 1]

                    await fish_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field, "**Bestiary**\n"))

                elif chosen_reaction == "⏹️":
                    await fish_message.clear_reactions()
                    break  # End the while loop

                elif chosen_reaction == "🔢":
                    number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")

                    # Check for custom message
                    def message_check(message):
                        return message.author == ctx.author and message.channel == fish_message.channel and message.content.isdigit()

                    user_message = await self.bot.wait_for('message', check=message_check)
                    user_input = int(user_message.content)

                    curr_index = min(len(fields), max(1, user_input))
                    curr_field = fields[curr_index - 1]

                    await fish_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field, "**Bestiary**\n"))
                    await number_message.delete()
                    await user_message.delete()

                    
        else:
            for rarity, fish_types in self.bot.fish.items():
                for fish_type, fish_info in fish_types.items():
                    if fish_info["name"] == str(fish_name.title()):
                        new_fish = fish_info
            embed = discord.Embed()
            embed.title = new_fish['name']
            embed.set_image(url="attachment://new_fish.png")
            embed.add_field(name='Rarity', value=f"This fish is {new_fish['rarity']}", inline=False)
            embed.add_field(name='Cost', value=f"This fish is {new_fish['cost']}", inline=False)
            embed.color = {
                # 0xHexCode
                "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
                "uncommon": 0x75FE66,  # Green
                "rare": 0x4AFBEF,  # Blue
                "epic": 0xE379FF,  # Light Purple
                "legendary": 0xFFE80D,  # Gold
                "mythic": 0xFF0090,  # Hot Pink
            }[new_fish['rarity']]
            fish_file = discord.File(new_fish["image"], "new_fish.png")
            await ctx.send(file=fish_file, embed=embed)

    def create_bucket_embed(self, user, field, title):
        embed = discord.Embed()  # Create a new embed to edit the message
        embed.title = title
        embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
        return embed

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def help(self, ctx: commands.Context, bot_command: typing.Optional[str]):
        """
        `a.help \"command(optional)\"` This command shows a helpful paragraph and when a command is specified gives information about the command.
        """
        cog_dict = {}
        for name, cog in self.bot.cogs.items():
            cog_dict[name] = {i.name: f"a.{i.name}\n{i.help}" for i in cog.walk_commands()}
        for cog, command_dict in cog_dict.items():
            for name_command, help_command in command_dict.items():
                if bot_command == name_command:
                    embed = discord.Embed(title=f"{name_command} command")
                    embed.add_field(name=cog, value=help_command)
                    await ctx.author.send(embed=embed)
                    return await ctx.send(f"Help for {name_command} DMed to you!")
        await ctx.author.send(HELP_TEXT_GENERAL)
        return await ctx.send("Help DMed to you!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def commands(self, ctx: commands.Context):
        """
        `a.commands` This shows you a list of all the commands you can use."""
        fields = []
        embed = discord.Embed(title="Commands (anything in quotes is a variable, and the quotes may or may not be needed)")
        cog_dict = {}
        for name, cog in self.bot.cogs.items():
            if name == "Jishaku":
                continue
            cog_dict[name] = {i.name: i.help for i in cog.walk_commands()}
        for cog, command_dict in cog_dict.items():
            cog_info = [help_command for _, help_command in command_dict.items()]
            fields.append((f"{cog} commands", "\n".join(cog_info)))
        # Create an embed
        curr_index = 1
        curr_field = fields[curr_index - 1]
        embed = self.create_info_embed(ctx.author, curr_field)

        command_message = await ctx.send(embed=embed)

        valid_reactions = ["◀️", "▶️", "⏹️", "🔢"]
        [await command_message.add_reaction(reaction) for reaction in valid_reactions]  # Add the pagination reactions to the message

        def reaction_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions and reaction.message == command_message

        while True:  # Keep paginating until the user clicks stop
            try:
                chosen_reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                chosen_reaction = chosen_reaction.emoji
            except asyncio.TimeoutError:
                chosen_reaction = "⏹️"
            
            index_chooser = {
                "◀️": max(1, curr_index - 1),
                "▶️": min(len(fields), curr_index + 1)
            }
            
            if chosen_reaction in index_chooser.keys():
                curr_index = index_chooser[chosen_reaction]  # Keep the index in bounds
                curr_field = fields[curr_index - 1]

                await command_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field, "Commands (anything in quotes is a variable, and the quotes may or may not be needed)"))

            elif chosen_reaction == "⏹️":
                await command_message.clear_reactions()
                break  # End the while loop

            elif chosen_reaction == "🔢":
                number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")

                # Check for custom message
                def message_check(message):
                    return message.author == ctx.author and message.channel == command_message.channel and message.content.isdigit()

                user_message = await self.bot.wait_for('message', check=message_check)
                user_input = int(user_message.content)

                curr_index = min(len(fields), max(1, user_input))
                curr_field = fields[curr_index - 1]

                await command_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field, "Commands (anything in quotes is a variable, and the quotes may or may not be needed)"))
                await number_message.delete()
                await user_message.delete()

    def create_info_embed(self, user, field):
        embed = discord.Embed()  # Create a new embed to edit the message
        embed.title = "Commands (anything in quotes is a variable, and the quotes may or may not be needed)"
        embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
        return embed
    








def setup(bot):
    bot.add_cog(Informative(bot))

