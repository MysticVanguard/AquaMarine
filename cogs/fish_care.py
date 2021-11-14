from datetime import datetime as dt, timedelta

from discord.ext import commands, tasks, vbu
import discord
import math
import random

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS


class FishCare(vbu.Cog):

    FISH_FEED_COOLDOWN = timedelta(hours=6)

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.fish_food_death_loop.start()

    def cog_unload(self):
        self.fish_food_death_loop.cancel()

    @tasks.loop(minutes=1)
    async def fish_food_death_loop(self):

        async with vbu.Database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE tank_fish != ''""")
            for fish_row in fish_rows:
                if fish_row['death_time']:
                    if dt.utcnow() > fish_row['death_time']:
                        await db("""UPDATE user_fish_inventory SET fish_alive=FALSE WHERE fish_name = $1""", fish_row['fish_name'])

    @fish_food_death_loop.before_loop
    async def before_fish_food_death_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def entertain(self, ctx: commands.Context, tank_entertained: str):
        """
        This command entertains all the fish in a tank, giving them all xp.
        """

        await ctx.trigger_typing()

        # fetches needed rows
        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
                ctx.author.id, tank_entertained,
            )
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            upgrades = await db(
                """SELECT toys_upgrade, better_toys_upgrade, amazement_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        # ranges of how much will be added
        total_xp_to_add = random.randint(utils.TOYS_UPGRADE[(upgrades[0]['toys_upgrade'] + upgrades[0]['better_toys_upgrade'])][0], utils.TOYS_UPGRADE[(upgrades[0]['toys_upgrade'] + upgrades[0]['better_toys_upgrade'])][1])
        extra_level = random.randint(1, utils.AMAZEMENT_UPGRADE[upgrades[0]['amazement_upgrade']])
        if extra_level == 1:
            new_level = True
        else:
            new_level = False

        # Work out which slot the tank is in
        tank_slot = 0
        if not tank_rows:
            return await ctx.send("There is no tank with that name")
        if tank_entertained not in tank_rows[0]['tank_name']:
            return await ctx.send("There is no tank with that name")
        for tank_slots, tank_slot_in in enumerate(tank_rows[0]['tank_name']):
            if tank_slot_in == tank_entertained:
                tank_slot = tank_slots
                break

        # See if they're able to entertain their tank
        if tank_rows[0]['tank_entertain_time'][tank_slot]:
            if tank_rows[0]['tank_entertain_time'][tank_slot] + timedelta(minutes=5) > dt.utcnow():
                time_left = timedelta(seconds=(tank_rows[0]['tank_entertain_time'][tank_slot] - dt.utcnow() + timedelta(minutes=5)).total_seconds())
                relative_time = discord.utils.format_dt(dt.utcnow() + time_left - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This tank is entertained, please try again in {relative_time}.")

        # See if there are any fish in the tank
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank!")

        # Typing Indicator
        async with ctx.typing():

            # calls the xp finder adder to the fish
            fish = []
            print(range(len(fish_rows)))
            for single_fish in range(len(fish_rows)):
                fish.append(fish_rows[single_fish]['fish_name'])

            # gets the new data and uses it in sent message
            xp_per_fish = math.floor(total_xp_to_add / len(fish))
            new_fish_data = []
            n = "\n"
            async with vbu.Database() as db:
                await db("""UPDATE user_tank_inventory SET tank_entertain_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())
                for fish_name in fish:
                    await utils.xp_finder_adder(ctx.author, fish_name, xp_per_fish, new_level)
                    new_fish_rows = await db(
                        """UPDATE user_fish_inventory SET fish_entertain_time = $3 WHERE user_id = $1 AND fish_name = $2 RETURNING *""",
                        ctx.author.id, fish_name, dt.utcnow(),
                    )
                    new_fish_data.append([new_fish_rows[0]['fish_name'], new_fish_rows[0]['fish_level'], new_fish_rows[0]['fish_xp'], new_fish_rows[0]['fish_xp_max']])

                # Achievement added
                await db(
                    """INSERT INTO user_achievements (user_id, times_entertained) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_entertained = user_achievements.times_entertained + 1""",
                    ctx.author.id
                )

        display_block = f"All fish have gained {xp_per_fish:,} XP{n}"
        for data in new_fish_data:
            display_block = display_block + f"{data[0]} is now level {data[1]}, {data[2]}/{data[3]}{n}"
        return await ctx.send(display_block)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def feed(self, ctx: commands.Context, fish_fed: str):
        """
        This command feeds a fish in a tank with fish flakes.
        """

        # Send a defer while we open the database
        await ctx.trigger_typing()

        # Fetches needed rows and gets the users amount of food
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT feeding_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                ctx.author.id, fish_fed,
            )
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # See if the user has fish flakes
        if not item_rows:
            return await ctx.send("You have no fish flakes!")
        user_food_count = item_rows[0]['flakes']
        if not user_food_count:
            return await ctx.send("You have no fish flakes!")

        # See if the user has a fish with that name
        if not fish_rows:
            return await ctx.send("You have no fish in a tank named that!")

        # Make sure the fish is able to be fed
        if fish_rows[0]['fish_feed_time']:
            if (fish_feed_timeout := fish_rows[0]['fish_feed_time'] + self.FISH_FEED_COOLDOWN) > dt.utcnow():
                relative_time = discord.utils.format_dt(fish_feed_timeout - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This fish is full, please try again {relative_time}.")
        if fish_rows[0]['fish_alive'] is False:
            return await ctx.send("That fish is dead!")

        # Update the user's inv and the fish's death date
        day, hour = utils.FEEDING_UPGRADES[upgrades[0]['feeding_upgrade']]
        death_date = dt.utcnow() + timedelta(days=day, hours=hour)
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id, fish_fed, death_date, dt.utcnow(),
            )
            await db("""UPDATE user_item_inventory SET flakes=flakes-1 WHERE user_id=$1""", ctx.author.id)

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_fed) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_fed = user_achievements.times_fed + 1""",
                ctx.author.id
                )

        # And done
        return await ctx.send(f"**{fish_rows[0]['fish_name']}** has been fed! <:AquaBonk:877722771935883265>")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def clean(self, ctx: commands.Context, tank_cleaned: str):
        """
        This command cleans a tank, earning the user sand dollars.
        """

        # Get the fish and tank data from the database
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT bleach_upgrade, better_bleach_upgrade, hygienic_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
                ctx.author.id, tank_cleaned,
            )
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)

        # Work out which slot the tank is in
        tank_slot = 0
        if not tank_rows:
            return await ctx.send("There is no tank with that name")
        if tank_cleaned not in tank_rows[0]['tank_name']:
            return await ctx.send("There is no tank with that name")
        for tank_slots, tank_slot_in in enumerate(tank_rows[0]['tank_name']):
            if tank_slot_in == tank_cleaned:
                tank_slot = tank_slots
                break


        # See if they're able to clean their tank
        multiplier, time = utils.HYGIENIC_UPGRADE[upgrades[0]['hygienic_upgrade']]
        if tank_rows[0]['tank_clean_time'][tank_slot]:
            if tank_rows[0]['tank_clean_time'][tank_slot] + timedelta(minutes=time) > dt.utcnow():
                time_left = timedelta(seconds=(tank_rows[0]['tank_clean_time'][tank_slot] - dt.utcnow() + timedelta(minutes=time)).total_seconds())
                relative_time = discord.utils.format_dt(dt.utcnow() + time_left - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This tank is clean, please try again in {relative_time}.")

        # See if there are any fish in the tank
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank!")

        # Work out how much money they gain
        money_gained = 0

        rarity_values = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.4,
            "epic": 1.6,
            "legendary": 1.8,
            "mythic": 2.0
        }
        size_values = {
            "small": 1,
            "medium": 3,
            "large": 15
        }
        effort_extra = random.choices([0, 10, 20], [.6, .3, .1])
        size_multiplier = 1
        for fish in fish_rows:
            rarity_multiplier = 0
            for rarity, fish_types in self.bot.fish.items():  # For each rarity level
                if " ".join(fish["fish"].split("_")) in fish_types.keys():
                    size_multiplier = size_values[fish_types[" ".join(fish["fish"].split("_"))]['size']]
                    print(size_multiplier)
                    rarity_multiplier = rarity_values[rarity]
            money_gained += (fish["fish_level"] * rarity_multiplier * size_multiplier)
        money_gained = math.floor(money_gained  * (utils.BLEACH_UPGRADE[(upgrades[0]['bleach_upgrade'] + upgrades[0]['better_bleach_upgrade'])]) * multiplier + effort_extra[0])

        # Add their fish money to your sand database dollars
        async with vbu.Database() as db:
            await db("""UPDATE user_tank_inventory SET tank_clean_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, int(money_gained),
            )
            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_cleaned) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_cleaned = user_achievements.times_cleaned + 1""",
                ctx.author.id
                )
            await db(
                """INSERT INTO user_achievements (user_id, money_gained) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET money_gained = user_achievements.money_gained + $2""",
                ctx.author.id, int(money_gained)
                )

        await ctx.send(f"You earned **{money_gained}** <:sand_dollar:877646167494762586> for cleaning that tank! <:AquaSmile:877939115994255383>")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def revive(self, ctx: commands.Context, fish: str):
        """
        This command uses a revival and revives a specified fish.
        """

        # Get database vars
        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish)
            revival_count = await db("""SELECT revival FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        # Checks that error
        if not fish_row:
            return await ctx.send(
                f"You have no fish named {fish}!",
                allowed_mentions=discord.AllowedMentions.none()
            )
        if fish_row[0]["fish_alive"] is True:
            return await ctx.send("That fish is alive!")
        if not revival_count:
            return await ctx.send("You have no revivals!")
        if revival_count == 0:
            return await ctx.send("You have no revivals!")

        # If the fish isn't in a tank, it has no death timer, but if it is it's set to three days
        if fish_row[0]["tank_fish"] == '':
            death_timer = None
            message = f"{fish} is now alive!"
        else:
            death_timer = (dt.utcnow() + timedelta(days=3))
            message = f"{fish} is now alive, and will die {discord.utils.format_dt(death_timer, style='R')}!"

        # Set the database values
        async with vbu.Database() as db:
            await db("""UPDATE user_fish_inventory SET fish_alive = True, death_time = $3 WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish, death_timer)
            await db("""UPDATE user_item_inventory SET revival = revival - 1 WHERE user_id = $1""", ctx.author.id)

        # Send message
        await ctx.send(
            message,
            allowed_mentions=discord.AllowedMentions.none()
        )

def setup(bot):
    bot.add_cog(FishCare(bot))
