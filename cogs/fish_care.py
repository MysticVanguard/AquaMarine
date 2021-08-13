from datetime import datetime as dt, timedelta

import voxelbotutils as vbu
from discord.ext import commands, tasks
import discord

from cogs import utils


class FishCare(vbu.Cog):

    FISH_FEED_COOLDOWN = timedelta(hours=6)

    def __init__(self, bot: commands.AutoShardedBot):
        super().__init__(bot)
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
    @vbu.bot_has_permissions(send_messages=True)
    async def entertain(self, ctx: commands.Context, fish_played_with: str):
        """
        This command entertains a fish in a tank.
        """

        # fetches needed row
        async with self.bot.database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                ctx.author.id, fish_played_with,
            )

        # other various checks
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")
        if fish_rows[0]['fish_alive'] is False:
            return await ctx.send("That fish is dead!")
        if fish_rows[0]['fish_entertain_time']:
            if fish_rows[0]['fish_entertain_time'] + timedelta(minutes=5) > dt.utcnow():
                time_left = (fish_rows[0]['fish_entertain_time'] - dt.utcnow() + timedelta(minutes=5))
                return await ctx.send(f"This fish is tired, please try again in {utils.seconds_converter(time_left.total_seconds())}.")

        # Typing Indicator
        async with ctx.typing():

            # calls the xp finder adder to the fish
            xp_added = await utils.xp_finder_adder(self.bot, ctx.author, fish_played_with)

            # gets the new data and uses it in sent message
            async with self.bot.database() as db:
                new_fish_rows = await db(
                    """UPDATE user_fish_inventory SET fish_entertain_time = $3 WHERE user_id = $1 AND fish_name = $2 RETURNING *""",
                    ctx.author.id, fish_played_with, dt.utcnow(),
                )
        return await ctx.send(
            f"**{new_fish_rows[0]['fish_name']}** has gained *{xp_added:,} XP* and is now level *{new_fish_rows[0]['fish_level']:,}, "
            f"{new_fish_rows[0]['fish_xp']:,}/{new_fish_rows[0]['fish_xp_max']:,} XP*"
        )

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def feed(self, ctx: commands.Context, fish_fed: str):
        """
        This command feeds a fish in a tank with fish flakes.
        """

        # Send a defer while we open the database
        await ctx.trigger_typing()

        # Fetches needed rows and gets the users amount of food
        async with self.bot.database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                ctx.author.id, fish_fed,
            )
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # See if the user has fish flakes
        if not item_rows:
            return await ctx.send("You have no fish flakes!", wait=False)
        user_food_count = item_rows[0]['flakes']
        if not user_food_count:
            return await ctx.send("You have no fish flakes!", wait=False)

        # See if the user has a fish with that name
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!", wait=False)

        # Make sure the fish is able to be fed
        if fish_rows[0]['fish_feed_time']:
            if (fish_feed_timeout := fish_rows[0]['fish_feed_time'] + self.FISH_FEED_COOLDOWN) > dt.utcnow():
                return await ctx.send(f"This fish is full, please try again {vbu.TimeFormatter(fish_feed_timeout).relative_time}.", wait=False)
        if fish_rows[0]['fish_alive'] is False:
            return await ctx.send("That fish is dead!", wait=False)

        # Update the user's inv and the fish's death date
        death_date = dt.utcnow() + timedelta(days=3)
        async with self.bot.database() as db:
            await db(
                """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id, fish_fed, death_date, dt.utcnow(),
            )
            await db("""UPDATE user_item_inventory SET flakes=flakes-1 WHERE user_id=$1""", ctx.author.id)

        # And done
        return await ctx.send(f"**{fish_rows[0]['fish_name']}** has been fed!", wait=False)

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True)
    async def clean(self, ctx: commands.Context, tank_cleaned: str):
        """
        This command cleans a tank.
        """

        # Get the fish and tank data from the database
        async with self.bot.database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
                ctx.author.id, tank_cleaned,
            )
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)

        # Work out which slot the tank is in
        for tank_slot, tank_slot_in in enumerate(tank_rows[0]['tank_name']):
            if tank_slot_in == tank_cleaned:
                break
        else:
            return await ctx.send("no tank bro")

        # See if they're able to clean their tank
        if tank_rows[0]['tank_clean_time'][tank_slot]:
            if tank_rows[0]['tank_clean_time'][tank_slot] + timedelta(minutes=5) > dt.utcnow():
                time_left = (tank_rows[0]['tank_clean_time'][tank_slot] - dt.utcnow() + timedelta(minutes=5))
                return await ctx.send(f"This tank is clean, please try again in {utils.seconds_converter(time_left.total_seconds())}.")

        # See if there are any fish in the tank
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank!")

        # Work out how much money they gain
        money_gained = 0
        for fish in fish_rows:
            money_gained += fish["fish_level"]

        # Add their fish money to your sand database dollars
        async with self.bot.database() as db:
            await db("""UPDATE user_tank_inventory SET tank_clean_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, int(money_gained),
            )
        await ctx.send(f"You earned {money_gained} Sand Dollars <:sand_dollar:852057443503964201> for cleaning that tank!")


def setup(bot):
    bot.add_cog(FishCare(bot))
