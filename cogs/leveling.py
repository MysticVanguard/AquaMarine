import random
import typing
import re
import asyncio
import math

import discord
from discord.ext import commands

import utils


class Leveling(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    # does all the xp stuff
    async def xp_finder_adder(self, user: discord.User, type_of_food, fed_fish):
        # ranges of how much will be added
        xp_amounts = {"flakes": (5, 10), "pellets": (15, 25), "wafers": (38, 75)}
        total_xp_to_add = random.randint(xp_amounts[type_of_food][0], xp_amounts[type_of_food][1])

        # initial acquired fish data
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", user.id, fed_fish)
        
        # for each tick of xp...
        for i in range(total_xp_to_add):

            # level increase xp calculator
            xp_per_level = math.floor(25 * fish_rows[0]['fish_level'] ** 1.5)

            # if the xp is higher or equal to the xp recquired to level up...
            if fish_rows[0]['fish_xp'] >= fish_rows[0]['fish_xp_max']:

                # update the level to increase by one, reset fish xp, and set fish xp max to the next level xp needed
                async with utils.DatabaseConnection() as db:
                    await db("""UPDATE user_fish_inventory SET fish_level = fish_level + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, fed_fish)
                    await db("""UPDATE user_fish_inventory SET fish_xp = 0 WHERE user_id = $1 AND fish_name = $2""", user.id, fed_fish)
                    await db("""UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""", int(xp_per_level), user.id, fed_fish)
            
            # adds one xp regets new fish_rows
            async with utils.DatabaseConnection() as db:
                fish_rows = await db("""UPDATE user_fish_inventory SET fish_xp = fish_xp + 1 WHERE user_id = $1 AND fish_name = $2 RETURNING *""", user.id, fed_fish)
        
        # returns xp gained
        return total_xp_to_add
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def feed(self, ctx: commands.Context, fish_food_type, fish_fed):
        """
            Feed your fish to give them XP (Use \"flakes\", \"pellets\", or \"wafers\" when feeding)
        """

        # food type options
        food_type = ["flakes", "pellets", "wafers"]
        
        # checks if the given food type is a food type
        if fish_food_type not in food_type:
            return await ctx.send(f"That is not a type of fish food!")
        
        # fetches needed rows and gets the users amount of food
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_fed)
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
            user_food_count = item_rows[0][fish_food_type]

        # other various checks
        if not fish_rows:
            return await ctx.send("You have no fish named that!")
        if not user_food_count:
            return await ctx.send(f"You have no fish {fish_food_type}!")

        #Typing Indicator
        async with ctx.typing():

            # uses one piece of food
            if fish_food_type == "flakes":
                async with utils.DatabaseConnection() as db:
                    await db("""UPDATE user_item_inventory SET flakes=flakes-1 WHERE user_id=$1""", ctx.author.id)
            if fish_food_type == "pellets":
                async with utils.DatabaseConnection() as db:
                    await db("""UPDATE user_item_inventory SET pellets=pellets-1 WHERE user_id=$1""", ctx.author.id)
            if fish_food_type == "wafers":
                async with utils.DatabaseConnection() as db:
                    await db("""UPDATE user_item_inventory SET wafers=wafers-1 WHERE user_id=$1""", ctx.author.id)
            
            # calls the xp finder adder to the fish
            xp_added = await self.xp_finder_adder(ctx.author, fish_food_type, fish_fed)

            # gets the new data and uses it in sent message
            async with utils.DatabaseConnection() as db:
                new_fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_fed)
        return await ctx.send(f"**{new_fish_rows[0]['fish_name']}** has gained *{str(xp_added)} XP* and is now level *{new_fish_rows[0]['fish_level']}, {new_fish_rows[0]['fish_xp']}/{new_fish_rows[0]['fish_xp_max']} XP*")



def setup(bot):
    bot.add_cog(Leveling(bot))
