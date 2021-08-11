
import asyncio
import typing

import discord
from discord.ext import commands
import voxelbotutils as vbu
from cogs import utils

class Informative(vbu.Cog):

    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        
    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def tanks(self, ctx: commands.Context):
        '''
        `a.tanks` shows information about the users tanks.
        '''
        die = '\n'
        count = 0
        async with self.bot.database() as db:
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

    @vbu.command()
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

        async with self.bot.database() as db:
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

        embed = vbu.Embed(title=f"{ctx.author.display_name}'s Profile")
        embed.set_thumbnail(url='https://imgur.com/a/7sGHrse')

        fields_dict = {
            'Collection': ("\n".join(collection_info), False),
            'Balance': (f'<:sand_dollar:852057443503964201>: {balance[0]["balance"]}x Sand Dollars', False),
            '# of Tanks': (number_of_tanks, False),
            'Highest Level Fish': (f'{highest_level_fish_emoji} {highest_level_fish["fish_name"]}: Lvl. {highest_level_fish["fish_level"]} {highest_level_fish["fish_xp"]}/ {highest_level_fish["fish_xp_max"]}', False),
            'Achievements':  ("Soon To Be Added.", True),
            'Owned Fish': (' '.join(fish_info), True),
            'Items': (' '.join(inventory_info), True),
        }
        
        for name, (text, inline) in fields_dict.items():
            embed.add_field(name=name, value=text, inline=inline)

        await ctx.send(embed=embed)

    @vbu.command()
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

            utils.paginate(ctx, fields, ctx.author, "**Bestiary**\n")
        
        else:
            for rarity, fish_types in self.bot.fish.items():
                for _, fish_info in fish_types.items():
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
    

def setup(bot):
    bot.add_cog(Informative(bot))

