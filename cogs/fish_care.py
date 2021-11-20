from datetime import datetime as dt, timedelta

from discord.ext import commands, tasks, vbu
import discord
import math
import random

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS


class FishCare(vbu.Cog):

    # Set the cooldown for feeding to 6 hours
    FISH_FEED_COOLDOWN = timedelta(hours=6)

    # Starts the death loop
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.fish_food_death_loop.start()

    # Cancels the death loop when the bot is off
    def cog_unload(self):
        self.fish_food_death_loop.cancel()

    # every minute...
    @tasks.loop(minutes=1)
    async def fish_food_death_loop(self):

        # Get all the fish that are in a tank and if they have a time of death, check to see if its past that time, then kill them if need be
        async with vbu.Database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE tank_fish != ''""")
            for fish_row in fish_rows:
                if fish_row['death_time']:
                    if dt.utcnow() > fish_row['death_time']:
                        await db("""UPDATE user_fish_inventory SET fish_alive=FALSE WHERE fish_name = $1""", fish_row['fish_name'])

    # Make sure it starts when the bot starts
    @fish_food_death_loop.before_loop
    async def before_fish_food_death_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def entertain(self, ctx: commands.Context, *, tank_entertained: str = None):
        """
        This command entertains all the fish in a tank, giving them all xp.
        """

        # fetches needed rows
        async with vbu.Database() as db:
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            upgrades = await db(
                """SELECT toys_upgrade, amazement_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        await ctx.trigger_typing()
        if not tank_entertained:

            # Create a select menu with the tanks as options
            tank_entertained = await utils.create_select_menu(
                self.bot, ctx, tank_rows[0]['tank_name'], "tank", "entertain")

        # Get the fish in the chosen tank
        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
                ctx.author.id, tank_entertained,
            )

        # Finds how much xp will be added, and if an extra level will be added
        total_xp_to_add = random.randint(
            utils.TOYS_UPGRADE[upgrades[0]['toys_upgrade']][0], utils.TOYS_UPGRADE[upgrades[0]['toys_upgrade']][1])
        extra_level = random.randint(
            1, utils.AMAZEMENT_UPGRADE[upgrades[0]['amazement_upgrade']])

        # set a new level check to true if theres an extra level
        if extra_level == 1:
            new_level = True
        else:
            new_level = False

        # Checks to see if there is no tank
        if tank_entertained not in tank_rows[0]['tank_name'] or not tank_rows:
            return await ctx.send("There is no tank with that name")

        # Work out which slot the tank is in
        tank_slot = 0
        for tank_slots, tank_slot_in in enumerate(tank_rows[0]['tank_name']):
            if tank_slot_in == tank_entertained:
                tank_slot = tank_slots
                break

        # See if they're able to entertain their tank due to the cooldown
        if tank_rows[0]['tank_entertain_time'][tank_slot]:
            if tank_rows[0]['tank_entertain_time'][tank_slot] + timedelta(minutes=5) > dt.utcnow():
                time_left = timedelta(seconds=(
                    tank_rows[0]['tank_entertain_time'][tank_slot] - dt.utcnow() + timedelta(minutes=5)).total_seconds())
                relative_time = discord.utils.format_dt(
                    dt.utcnow() + time_left - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This tank is entertained, please try again in {relative_time}.")

        # See if there are any fish in the tank
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank!")

        # Typing Indicator
        async with ctx.typing():

            # For each fish add them to a list of fish names
            fish = []
            for single_fish in range(len(fish_rows)):
                fish.append(fish_rows[single_fish]['fish_name'])
            print(fish)

            # Find the xp per fish and initiate the new data, and new line
            xp_per_fish = math.floor(total_xp_to_add / len(fish))
            new_fish_data = []
            n = "\n"

            # database...
            async with vbu.Database() as db:

                # Set the new time for when the tank was entertained
                await db("""UPDATE user_tank_inventory SET tank_entertain_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())

                # For each fish in the tank add their xp, gets the new fish's data
                for fish_name in fish:
                    await utils.xp_finder_adder(ctx.author, fish_name, xp_per_fish, new_level)
                    new_fish_rows = await db(
                        """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                        ctx.author.id, fish_name,
                    )
                    new_fish_data.append([new_fish_rows[0]['fish_name'], new_fish_rows[0]['fish_level'],
                                         new_fish_rows[0]['fish_xp'], new_fish_rows[0]['fish_xp_max']])

                # Achievement added
                await db(
                    """INSERT INTO user_achievements (user_id, times_entertained) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_entertained = user_achievements.times_entertained + 1""",
                    ctx.author.id
                )

        # The start of the display
        display_block = f"All fish have gained {xp_per_fish:,} XP{n}"

        # Add a string for each fish adding their new level and data
        for data in new_fish_data:
            display_block = display_block + \
                f"{data[0]} is now level {data[1]}, {data[2]}/{data[3]}{n}"

        # Send the display string
        return await ctx.send(display_block)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def feed(self, ctx: commands.Context, *, fish_fed: str = None):
        """
        This command feeds a fish in a tank with fish flakes.
        """

        # Send a defer while we open the database
        await ctx.trigger_typing()

        # Fetches needed rows and gets the users amount of food
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT feeding_upgrade, big_servings_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish != ''""",
                ctx.author.id,
            )
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)
            item_rows = await db("""SELECT * FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        await ctx.trigger_typing()

        if not fish_fed:

            # If they own more than 25 fish...
            if len(fish_rows) > 25:

                # Creates a select menu of all the tanks and returns the users choice
                tank_chosen = await utils.create_select_menu(
                    self.bot, ctx, tank_rows[0]['tank_name'], "tank", "choose")

                # Set the new fish_rows of only fish in that tank
                async with vbu.Database() as db:
                    fish_rows = await db(
                        """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""",
                        ctx.author.id, tank_chosen
                    )

            fish_in_tank = []
            for fish in fish_rows:
                fish_in_tank.append(fish["fish_name"])

            fish_fed = await utils.create_select_menu(
                self.bot, ctx, fish_in_tank, "fish", "feed")

        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                ctx.author.id, fish_fed,
            )

        # See if the user has fish flakes
        if fish_row[0]['fish_level'] <= 20:
            type_of_food = "flakes"
        elif fish_row[0]['fish_level'] <= 50:
            type_of_food = "pellets"
        else:
            type_of_food = "wafers"
        user_food_count = item_rows[0][type_of_food]
        if not item_rows or not user_food_count:
            return await ctx.send(f"You have no {type_of_food}!")

        # See if the user has a fish with that name
        if not fish_row:
            return await ctx.send("You have no fish in a tank named that!")

        # Make sure the fish is able to be fed
        if fish_row[0]['fish_feed_time']:
            if (fish_feed_timeout := fish_row[0]['fish_feed_time'] + self.FISH_FEED_COOLDOWN) > dt.utcnow() and ctx.author.id != 449966150898417664:
                relative_time = discord.utils.format_dt(
                    fish_feed_timeout - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This fish is full, please try again {relative_time}.")

        # Make sure the fish is alive
        if fish_row[0]['fish_alive'] is False:
            return await ctx.send("That fish is dead!")

        # How many days and hours till the next feed based on upgrades
        day, hour = utils.FEEDING_UPGRADES[upgrades[0]['feeding_upgrade']]

        # Set the time to be now + the new death date
        death_date = fish_row[0]['death_time'] + \
            timedelta(days=day, hours=hour)

        # Update the fish's death date
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id, fish_fed, death_date, dt.utcnow(),
            )

            # If the fish is full it doesn't take up fish food (calculated with upgrades)
            extra = ""
            full = random.randint(
                1, utils.BIG_SERVINGS_UPGRADE[upgrades[0]['big_servings_upgrade']])
            if full != 1:
                await db("""UPDATE user_item_inventory SET {0}={0}-1 WHERE user_id=$1""".format(type_of_food), ctx.author.id)
            else:
                extra = "\nThat fish wasn't as hungry and didn't consume food!"

            # Achievements
            await db(
                """INSERT INTO user_achievements (user_id, times_fed) VALUES ($1, 1)
                ON CONFLICT (user_id) DO UPDATE SET times_fed = user_achievements.times_fed + 1""",
                ctx.author.id
            )

        # And done
        return await ctx.send(f"**{fish_row[0]['fish_name']}** has been fed! <:AquaBonk:877722771935883265>{extra}")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def clean(self, ctx: commands.Context, *, tank_cleaned: str = None):
        """
        This command cleans a tank, earning the user sand dollars.
        """

        # Get the fish, upgrades, and tank data from the database
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT bleach_upgrade, hygienic_upgrade, mutation_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            tank_rows = await db("""SELECT * FROM user_tank_inventory WHERE user_id = $1""", ctx.author.id)

        if not tank_cleaned:

            # Creates a select menu of all the tanks and returns the users choice
            tank_cleaned = await utils.create_select_menu(
                self.bot, ctx, tank_rows[0]['tank_name'], "tank", "clean")

        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
                ctx.author.id, tank_cleaned,
            )

        # Find if the tank exists
        if not tank_rows:
            return await ctx.send("There is no tank with that name")
        if tank_cleaned not in tank_rows[0]['tank_name']:
            return await ctx.send("There is no tank with that name")

         # Work out which slot the tank is in
        tank_slot = 0
        for tank_slots, tank_slot_in in enumerate(tank_rows[0]['tank_name']):
            if tank_slot_in == tank_cleaned:
                tank_slot = tank_slots
                break

        # Get the time before cleaning and the multiplier from upgrades
        multiplier, time = utils.HYGIENIC_UPGRADE[upgrades[0]
                                                  ['hygienic_upgrade']]

        # If its been enough time they can clean, else give an error
        if tank_rows[0]['tank_clean_time'][tank_slot]:
            if tank_rows[0]['tank_clean_time'][tank_slot] + timedelta(minutes=time) > dt.utcnow() and ctx.author.id != 449966150898417664:
                time_left = timedelta(seconds=(
                    tank_rows[0]['tank_clean_time'][tank_slot] - dt.utcnow() + timedelta(minutes=time)).total_seconds())
                relative_time = discord.utils.format_dt(
                    dt.utcnow() + time_left - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This tank is clean, please try again {relative_time}.")

        # See if there are any fish in the tank
        if not fish_rows:
            return await ctx.send("You have no alive fish in this tank!")

        # Initiate money gained, the rarity multiplier, and the size multiplier dictionaries
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

        # Randomly pick the effort extra
        effort_extra = random.choices([0, 10, 20], [.6, .3, .1])

        # Initiate the size, extra, and rarity variables
        size_multiplier = 1
        extra = ""
        rarity_multiplier = 0

        # For each fish in the tank...
        for fish in fish_rows:

            fish_name = utils.get_normal_name(fish["fish"])

            # See if they mutate with the mutate upgrade
            mutate = random.randint(
                1, utils.MUTATION_UPGRADE[upgrades[0]['mutation_upgrade']])
            if mutate == 1 and fish_name == fish["fish"]:
                async with vbu.Database() as db:
                    mutated = "inverted_"+fish["fish"]
                    await db("""UPDATE user_fish_inventory SET fish = $1 where user_id = $2 AND fish = $3""", mutated, ctx.author.id, fish["fish"])
                    nl = "\n"
                    extra += f"{nl}{fish['fish']}looks kind of strange now..."

            # For each rarity of fish in the bot if the current fish is in it...
            for rarity, fish_types in self.bot.fish.items():
                if " ".join(fish_name.split("_")) in fish_types.keys():

                    # Grab the size of the fish
                    size_multiplier = size_values[fish_types[" ".join(
                        fish_name.split("_"))]['size']]

                    # Grab the rarity of the fish
                    rarity_multiplier = rarity_values[rarity]

            # The money added for each fish is the level * the rarity * the size
            money_gained += (fish["fish_level"] *
                             rarity_multiplier * size_multiplier)

        # After all the fish the new money is the total * upgrade multipliers + the effort rounded down
        money_gained = math.floor(
            money_gained * (utils.BLEACH_UPGRADE[upgrades[0]['bleach_upgrade']]) * multiplier + effort_extra[0])

        # Add the money gained to the database, and add the achievements
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

        # And were done, send it worked
        await ctx.send(f"You earned **{money_gained}** <:sand_dollar:877646167494762586> for cleaning that tank! <:AquaSmile:877939115994255383>{extra}")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def revive(self, ctx: commands.Context, *, fish: str = None):
        """
        This command uses a revival and revives a specified fish.
        """

        # Get database vars
        async with vbu.Database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_alive = FALSE""", ctx.author.id)
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish)
            revival_count = await db("""SELECT revival FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

        if not fish:

            fish_in_tank = []
            for fish in fish_rows:
                fish_in_tank.append(fish["fish_name"])

            fish = await utils.create_select_menu(
                self.bot, ctx, fish_in_tank, "dead fish", "revive")

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
