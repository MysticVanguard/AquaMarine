import random
import asyncio
import math
from datetime import datetime as dt, timedelta
import io
from PIL import Image
import imageio
import voxelbotutils as vbu

import discord
from discord.ext import commands, tasks

from cogs import utils

class Fish_Care(vbu.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.fish_food_death_loop.start()

    def cog_unload(self):
        self.fish_food_death_loop.cancel()

    @tasks.loop(minutes=1)
    async def fish_food_death_loop(self):

        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE tank_fish != ''""")
            for fish_row in fish_rows:
                if fish_row['death_time']:
                    if dt.utcnow() > fish_row['death_time']:
                        await db("""UPDATE user_fish_inventory SET fish_alive=TRUE WHERE fish_name = $1""", fish_row['fish_name'])

    @fish_food_death_loop.before_loop
    async def before_fish_food_death_loop(self):
        await self.bot.wait_until_ready()

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def entertain(self, ctx: commands.Context, fish_played_with):
        """
        This command entertains a fish in a tank.
        """
        # fetches needed row
        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""", ctx.author.id, fish_played_with)


        # other various checks
        if fish_rows[0]['fish_entertain_time']:
            if fish_rows[0]['fish_entertain_time'] + timedelta(minutes=5) > dt.utcnow():
                time_left = (fish_rows[0]['fish_entertain_time'] - dt.utcnow() + timedelta(minutes=5))
                return await ctx.send(f"This fish is tired, please try again in {utils.seconds_converter(time_left.total_seconds())}.")
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")
        if fish_rows[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")

        #Typing Indicator
        async with ctx.typing():

            # calls the xp finder adder to the fish
            xp_added = await utils.xp_finder_adder(ctx.author, fish_played_with)

            # gets the new data and uses it in sent message
            async with self.bot.database() as db:
                await db("""UPDATE user_fish_inventory SET fish_entertain_time = $3 WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_played_with, dt.utcnow())
                new_fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_played_with)
        return await ctx.send(f"**{new_fish_rows[0]['fish_name']}** has gained *{str(xp_added)} XP* and is now level *{new_fish_rows[0]['fish_level']}, {new_fish_rows[0]['fish_xp']}/{new_fish_rows[0]['fish_xp_max']} XP*")

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def feed(self, ctx: commands.Context, fish_fed):
        """
        This command feeds a fish in a tank with fish flakes.
        """

        # fetches needed rows and gets the users amount of food
        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""", ctx.author.id, fish_fed)
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
            user_food_count = item_rows[0]['flakes']

        # other various checks
        if fish_rows[0]['fish_feed_time']:
            if fish_rows[0]['fish_feed_time'] + timedelta(hours=6) > dt.utcnow():
                time_left = (fish_rows[0]['fish_feed_time'] - dt.utcnow() + timedelta(hours=6))
                return await ctx.send(f"This fish is full, please try again in {utils.seconds_converter(time_left.total_seconds())}.")
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")
        if not user_food_count:
            return await ctx.send("You have no fish flakes!")
        if fish_rows[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")

        #Typing Indicator
        async with ctx.typing():

            death_date = dt.utcnow() + timedelta(days=3)

            async with self.bot.database() as db:
                await db("""UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_fed, death_date, dt.utcnow())
                await db("""UPDATE user_item_inventory SET flakes=flakes-1 WHERE user_id=$1""", ctx.author.id)

        return await ctx.send(f"**{fish_rows[0]['fish_name']}** has been fed!")

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def clean(self, ctx: commands.Context, tank_cleaned):
        """
        This command cleans a tank.
        """
        money_gained = 0
        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""", ctx.author.id, tank_cleaned)
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
        tank_slot = 0
        for tank_slot_in in tank_rows[0]['tank_name']:
            if tank_slot_in == tank_cleaned:
                break
            else:
                tank_slot += 1
        if tank_rows[0]['tank_clean_time'][tank_slot]:
            if tank_rows[0]['tank_clean_time'][tank_slot] + timedelta(minutes=5) > dt.utcnow():
                time_left = (tank_rows[0]['tank_clean_time'][tank_slot] - dt.utcnow() + timedelta(minutes=5))
                return await ctx.send(f"This tank is clean, please try again in {utils.seconds_converter(time_left.total_seconds())}.")
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank, or it does not exist!")
        for fish in fish_rows:
            money_gained += fish["fish_level"]
        async with self.bot.database() as db:
            await db("""UPDATE user_tank_inventory SET tank_clean_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, int(money_gained),
                )
        await ctx.send(f"You earned {money_gained} Sand Dollars <:sand_dollar:852057443503964201> for cleaning that tank!")

def setup(bot):
    bot.add_cog(Fish_Care(bot))