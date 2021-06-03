import random
import typing
import re
import asyncio
from discord.utils import get
import discord
from discord.ext import commands
import utils

# Dict of fish emojis
emoji_rarities = {
    "common": {"clownfish": "849777027174760448", "goldfish": "849777027258515456", "tiger_barb": "849777027413311508", "royal_blue_betta": "849777027472031764", "pufferfish": "849777027501522954", "oscar_cichlid": "849777027599040522", "neon_tetra_school": "849777027326017586"},
    "uncommon": {"flowerhorn_cichlid": "849777027472293918", "lionfish": "849777027765633024"},
    "rare": {"axolotl": "850080397450149888"},
    "epic": {"asian_arowana": "850080397350010930"},
    "legendary": {"anglerfish": "849777027769696297"},
    "mythic": {"mandarinfish": "850080397081182269"}
}

class Slots(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def slots(self, ctx: commands.Context):
        """
        Rolls the slots
        """


        # See if the user has enough money
        if not await utils.check_price(ctx.author.id, 5):
                return await ctx.send("You don't have enough money for this! (5)")


        # Remove money from the user
        async with utils.DatabaseConnection() as db:
            await db("""
                UPDATE user_balance SET balance=balance-5 WHERE user_id = $1""", ctx.author.id)


        # Chooses the random fish for nonwinning rows
        chosen_fish = []
        rarities_of_fish = []
        for i in (range(9)):
            rarity_random = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]
            new_fish = random.choice(list(emoji_rarities[rarity_random]))
            rarities_of_fish.append(rarity_random)
            chosen_fish.append(new_fish)
        
        # Chooses winning fish
        rarity = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]
        fish_type = random.choice(list(emoji_rarities[rarity]))
        emoji_id = emoji_rarities[rarity][fish_type]

        # Find's the dict of winning fish
        fish_random_name = fish_type.replace("_", " ")
        used_fish =  self.bot.fish[rarity][fish_random_name]

        # Checks if the user won
        win_or_lose = random.randint(1, 10)


        # Sends embed of either winning roll or losing roll
        embed = discord.Embed()
        embed.title=f"{ctx.author.display_name}'s roll..."
        row = []
        if win_or_lose == 2:
            for i in range(0, 6, 3):
                row.append(f"<:{chosen_fish[i]}:{emoji_rarities[rarities_of_fish[i]][chosen_fish[i]]}><:{chosen_fish[i+1]}:{emoji_rarities[rarities_of_fish[i+1]][chosen_fish[i+1]]}><:{chosen_fish[i+2]}:{emoji_rarities[rarities_of_fish[i+2]][chosen_fish[i+2]]}>")
            row.append(f"<:{fish_type}:{emoji_id}><:{fish_type}:{emoji_id}><:{fish_type}:{emoji_id}>")
            embed.add_field(name="*spent 5*", value="\n".join(row), inline=False)
            embed.add_field(name="Lucky", value=f"You won {fish_random_name.title()} :)", inline=False)
            message = await ctx.send(embed=embed)
            await self.bot.get_cog("Fishing").ask_to_sell_fish(ctx.author, message, used_fish)
        else:
            for i in range(0, 9, 3):
                row.append(f"<:{chosen_fish[i]}:{emoji_rarities[rarities_of_fish[i]][chosen_fish[i]]}><:{chosen_fish[i+1]}:{emoji_rarities[rarities_of_fish[i+1]][chosen_fish[i+1]]}><:{chosen_fish[i+2]}:{emoji_rarities[rarities_of_fish[i+2]][chosen_fish[i+2]]}>")
            embed.add_field(name="*spent 5*", value="\n".join(row), inline=False)
            embed.add_field(name="Unlucky", value="You lost :(")
            await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Slots(bot))


