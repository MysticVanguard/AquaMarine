import discord
import utils
import random
import asyncio
import typing
from discord.ext import commands

class Bestiary(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx:commands.Context, fish_name):
        '''Gets info on fish specified'''
        new_fish = {}
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
            "common": 0xFFFFFE, # White - FFFFFF doesn't work with Discord
            "uncommon": 0x75FE66, # Green
            "rare": 0x4AFBEF, # Blue
            "epic": 0xE379FF, # Light Purple
            "legendary": 0xFFE80D, # Gold
            "mythic": 0xFF0090 # Hot Pink
        }[new_fish['rarity']]
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        await ctx.send(file=fish_file, embed=embed)
def setup(bot):
    bot.add_cog(Bestiary(bot))