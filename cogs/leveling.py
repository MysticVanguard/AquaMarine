import random
import typing
import re
import asyncio
import math
from datetime import datetime as dt, timedelta

import discord
from discord.ext import commands, tasks

import utils


class Leveling(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.fish_food_death_loop.start()

    def cog_unload(self):
        self.fish_food_death_loop.cancel()

    # does all the xp stuff
    async def xp_finder_adder(self, user: discord.User, played_with_fish):
        # ranges of how much will be added
        total_xp_to_add = random.randint(1, 25)

        # initial acquired fish data
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
        
        # for each tick of xp...
        for i in range(total_xp_to_add):

            # level increase xp calculator
            xp_per_level = math.floor(25 * fish_rows[0]['fish_level'] ** 1.5)

            # if the xp is higher or equal to the xp recquired to level up...
            if fish_rows[0]['fish_xp'] >= fish_rows[0]['fish_xp_max']:

                # update the level to increase by one, reset fish xp, and set fish xp max to the next level xp needed
                async with utils.DatabaseConnection() as db:
                    await db("""UPDATE user_fish_inventory SET fish_level = fish_level + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                    await db("""UPDATE user_fish_inventory SET fish_xp = 0 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                    await db("""UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""", int(xp_per_level), user.id, played_with_fish)
            
            # adds one xp regets new fish_rows
            async with utils.DatabaseConnection() as db:
                fish_rows = await db("""UPDATE user_fish_inventory SET fish_xp = fish_xp + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
    
        return total_xp_to_add

    @tasks.loop(minutes=1)
    async def fish_food_death_loop(self):
        
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE tank_fish != ''""")
            for fish_row in fish_rows:
                if fish_row['death_days']:
                    if dt.utcnow() > fish_row['death_days']:
                        await db("""UPDATE user_fish_inventory SET fish_alive=TRUE WHERE fish_name = $1 RETURNING fish_alive""", fish_row['fish_name'])      

    @fish_food_death_loop.before_loop
    async def before_fish_food_death_loop(self):
        await self.bot.wait_until_ready()


    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def death(self, ctx: commands.Context, fish_name):
        async with utils.DatabaseConnection() as db:
            await db("""UPDATE user_fish_inventory SET death_days=$1 WHERE fish_name = $2""", dt(1900, 12, 12), fish_name) 



    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(1, 1 * 60, commands.BucketType.user)
    async def entertain(self, ctx: commands.Context, fish_played_with):
        """
        Play with your fish!
        """        
        # fetches needed row
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""", ctx.author.id, fish_played_with)


        # other various checks
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")
        if fish_rows[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")

        #Typing Indicator
        async with ctx.typing():

            
            # calls the xp finder adder to the fish
            xp_added = await self.xp_finder_adder(ctx.author, fish_played_with)

            # gets the new data and uses it in sent message
            async with utils.DatabaseConnection() as db:
                new_fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_played_with)
        return await ctx.send(f"**{new_fish_rows[0]['fish_name']}** has gained *{str(xp_added)} XP* and is now level *{new_fish_rows[0]['fish_level']}, {new_fish_rows[0]['fish_xp']}/{new_fish_rows[0]['fish_xp_max']} XP*")

    @entertain.error
    async def entertain_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = error.retry_after
        if 5_400 > time >= 3_600:
            form = 'hour'
            time /= 60 * 60
        elif time > 3_600:
            form = 'hours'
            time /= 60 * 60
        elif 90 > time >= 60:
            form = 'minute'
            time /= 60
        elif time >= 60:
            form = 'minutes'
            time /= 60
        elif time < 1.5:
            form = 'second'
        else:
            form = 'seconds'
        await ctx.send(f'This fish is tired, please try again in {round(time)} {form}.')

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(1, 12 * 60 * 60, commands.BucketType.user)
    async def feed(self, ctx: commands.Context, fish_fed):
        """
            Feed your fish to make sure they survive
        """
        
        # fetches needed rows and gets the users amount of food
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""", ctx.author.id, fish_fed)
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
            user_food_count = item_rows[0]['flakes']

        # other various checks
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")
        if not user_food_count:
            return await ctx.send("You have no fish flakes!")
        if fish_rows[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")

        #Typing Indicator
        async with ctx.typing():
            
            death_date = dt.utcnow() + timedelta(days=3)

            async with utils.DatabaseConnection() as db:
                await db("""UPDATE user_fish_inventory SET fish_days = $1, death_days = $4 WHERE user_id = $2 AND fish_name = $3""", dt.utcnow(), ctx.author.id, fish_fed, death_date)
                await db("""UPDATE user_item_inventory SET flakes=flakes-1 WHERE user_id=$1""", ctx.author.id)



        return await ctx.send(f"**{fish_rows[0]['fish_name']}** has been fed!")

    @feed.error
    async def feed_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = error.retry_after
        if 5_400 > time >= 3_600:
            form = 'hour'
            time /= 60 * 60
        elif time > 3_600:
            form = 'hours'
            time /= 60 * 60
        elif 90 > time >= 60:
            form = 'minute'
            time /= 60
        elif time >= 60:
            form = 'minutes'
            time /= 60
        elif time < 1.5:
            form = 'second'
        else:
            form = 'seconds'
        await ctx.send(f'This fish isn\'t hungry, please try again in {round(time)} {form}.')
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @commands.cooldown(1,  5 * 60, commands.BucketType.user)
    async def clean(self, ctx: commands.Context, tank_cleaned):
        money_gained = 0
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""", ctx.author.id, tank_cleaned)
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank, or it does not exist!")
        for fish in fish_rows:
            money_gained += fish["fish_level"]

    @clean.error
    async def clean_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = error.retry_after
        if 5_400 > time >= 3_600:
            form = 'hour'
            time /= 60 * 60
        elif time > 3_600:
            form = 'hours'
            time /= 60 * 60
        elif 90 > time >= 60:
            form = 'minute'
            time /= 60
        elif time >= 60:
            form = 'minutes'
            time /= 60
        elif time < 1.5:
            form = 'second'
        else:
            form = 'seconds'
        await ctx.send(f'This tank is cleaned, please try again in {round(time)} {form}.')

def setup(bot):
    bot.add_cog(Leveling(bot))
