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


class Aquarium(vbu.Cog):

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
            money_gained += (fish["fish_level"] * 5)
        async with self.bot.database() as db:
            await db("""UPDATE user_tank_inventory SET tank_clean_time[$2] = $3 WHERE user_id = $1""", ctx.author.id, int(tank_slot + 1), dt.utcnow())
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                ctx.author.id, int(money_gained),
                )
        await ctx.send(f"You earned {money_gained} Sand Dollars <:sand_dollar:852057443503964201> for cleaning that tank!")


    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def firsttank(self, ctx:commands.Context):
        """
        This command gives you your first tank.
        """

        # See if they already have a tank
        async with self.bot.database() as db:
            fetched = await db("""SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
        if fetched:
            return await ctx.send("You have your first tank already!")

        type_of_tank = "Fish Bowl"
        # Add a tank to the user
        async with self.bot.database() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES ($1);""", ctx.author.id)
            await db(
                """UPDATE user_tank_inventory SET tank[1]=TRUE, tank_type[1]=$2,
                fish_room[1] = 1, tank_theme[1] = 'Aqua' WHERE user_id=$1""", ctx.author.id, type_of_tank)

        # Ask the user what they want to name their tank
        def check(message):
            return all([
                message.author == ctx.author,
                message.channel == ctx.channel,
                message.content,
                len(message.content) <= 32,
                message.content != "none",
            ])
        await ctx.send("What do you want to name your first tank? (32 character limit and cannot be \"none\")")
        try:
            name_message = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name_message.content
            await ctx.send(f"You have your new tank, **{name}**!")
        except asyncio.TimeoutError:
            name = "Starter Tank"
            await ctx.send((
                f"Did you forget about me {ctx.author.mention}? I've been waiting for a while "
                f"now! I'll name the tank for you. Let's call it **{name}**"
            ))

        # Save their tank name
        async with self.bot.database() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_name[1]=$1 WHERE user_id=$2;""",
                name, ctx.author.id,
            )

    @vbu.command(aliases=["dep"])
    @commands.bot_has_permissions(send_messages=True)
    async def deposit(self, ctx:commands.Context, tank_name, fish_deposited):
        '''
        This command deposits a specified fish into a specified tank.
        '''

        # variables for size value and the slot the tank is in
        size_values = {"small": 1, "medium": 5, "large": 10}
        tank_slot = 0

        # fetches the two needed rows from the database
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_deposited)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

        # all the checks for various reasons the command shouldn't be able to work
        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_deposited}!")
        if tank_name not in tank_row[0]['tank_name']:
            return await ctx.send(f"You have no tank named {tank_name}!")
        if not tank_row or tank_row[0]['tank'] == ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False']:
            return await ctx.send(f"You have no tanks!")
        if fish_row[0]['tank_fish']:
            return await ctx.send("This fish is already in a tank!")
        if fish_row[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")


        # finds the tank slot the tank in question is at
        for tank_slot_in in tank_row[0]['tank_name']:
            if tank_slot_in == tank_name:
                break
            else:
                tank_slot += 1

        # another check
        if tank_row[0]["fish_room"][tank_slot] < size_values[fish_row[0]["fish_size"]]:
            return await ctx.send(f"You have no room in that tank!")

        # tank slot has one added as python indexes start at 0 but database start at 1
        tank_slot += 1


        # add the fish to the tank in the database
        async with self.bot.database() as db:
            await db(
                """UPDATE user_tank_inventory SET fish_room[$2] = fish_room[$2] - $3 WHERE user_id=$1""", ctx.author.id, tank_slot, int(size_values[fish_row[0]["fish_size"]]))
            await db(
            """UPDATE user_fish_inventory SET tank_fish = $3, death_time = $4 WHERE fish_name=$1 AND user_id=$2""", fish_deposited, ctx.author.id, tank_name, (dt.utcnow() + timedelta(days=3)))
        return await ctx.send("Fish deposited!")

    @vbu.command(aliases=["rem"])
    @commands.bot_has_permissions(send_messages=True)
    async def remove(self, ctx:commands.Context, tank_name, fish_removed):
        '''
        This command removes a specified fish from a specified tank.
        '''
        # variables for size value and the slot the tank is in
        size_values = {"small": 1, "medium": 5, "large": 10}
        tank_slot = 0

        # fetches the two needed rows from the database
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish = $3""", ctx.author.id, fish_removed, tank_name)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_removed} in that tank!")
        if not tank_row or tank_row[0]['tank'] == ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False']:
            return await ctx.send(f"You have no tanks!")
        if fish_row[0]['fish_alive'] == False:
            return await ctx.send("That fish is dead!")

        # finds the tank slot the tank in question is at
        for tank_slot_in in tank_row[0]['tank_name']:
            if tank_slot_in == tank_name:
                break
            else:
                tank_slot += 1

        # dumb
        tank_slot += 1

        async with self.bot.database() as db:
            await db("""UPDATE user_fish_inventory SET tank_fish = '' WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_removed)
            await db("""UPDATE user_tank_inventory SET fish_room[$3] = fish_room[$3] + $2 WHERE user_id = $1""", ctx.author.id, int(size_values[fish_row[0]['fish_size']]), tank_slot)
        return await ctx.send(f"{fish_removed} removed from {tank_name}!")

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True)
    async def sell(self, ctx:commands.Context, fish_sold):
        '''
        This command sells the specified fish, and it must be out of a tank.
        '''
        cost = 0
        async with self.bot.database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_sold)

        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_sold}!")
        if fish_row[0]['tank_fish']:
            return await ctx.send("That fish is in a tank, please remove it to sell it.")
        multiplier = fish_row[0]['fish_level'] / 10
        for rarity, fish_types in self.bot.fish.items():
            for fish_type, fish_info in fish_types.items():
                if fish_info["raw_name"] == utils.get_normal_name(fish_row[0]['fish']):
                    cost = int(fish_info['cost'])
        sell_money = int(cost * (1 + multiplier))
        async with self.bot.database() as db:
            await db(
                    """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                    ctx.author.id, sell_money,
                )
            await db("""DELETE FROM user_fish_inventory WHERE user_id=$1 AND fish_name = $2""", ctx.author.id, fish_sold)
        await ctx.send(f"You have sold {fish_sold} for {sell_money} Sand Dollars <:sand_dollar:852057443503964201>!")

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def show(self, ctx:commands.Context, *, tank_name):
        """
        This command produces a gif of the specified tank.
        """
        #Typing Indicator
        async with ctx.typing():

            # variables
            move_x = []
            min_max_y = {"Fish Bowl": (20, 50), "Small Tank": (15, 200), "Medium Tank": (20, 200)}
            min_max_x = {"Fish Bowl": (-180, 150), "Small Tank": (-180, 360), "Medium Tank": (-800, 720)}
            fish_size_speed = {'Fish Bowl': 17, 'Small Tank': 18, 'Medium Tank': 25}
            im = []
            fishes = {}
            fish_y_value = []
            files = []
            golden_inverted_normal = 'normal'
            fish_selections = []
            gif_name = random.randint(1, 1000)
            tank_types = {"Fish Bowl": "fishbowl", "Small Tank": "Small_Tank_2D", "Medium Tank": "Medium_Tank_2D"}
            tank_slot = 0

            # gets database info for tank
            async with self.bot.database() as db:
                selected_fish = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""", ctx.author.id, tank_name)
                tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)


            # finds the tank slot
            for tank_slot_in in tank_row[0]['tank_name']:
                if tank_slot_in == tank_name:
                    break
                else:
                    tank_slot += 1
            # finds the type of tank it is
            tank_info = tank_row[0]['tank_type'][tank_slot]


            # finds what type of fish it is, then adds the paths to a list, as well as finding the fish's random starting position
            for selected_fish_types in selected_fish:
                fishes[selected_fish_types['fish']] = []
            for name, info in fishes.items():
                if "golden" in name:
                        fishes[name].append(name.lstrip("golden_"))
                        name = name.lstrip("golden_")
                        golden_inverted_normal = 'golden'
                if "inverted" in name:
                        fishes[name].append(name.lstrip("inverted_"))
                        name = name.lstrip("inverted_")
                        golden_inverted_normal = 'inverted'
                else:
                    fishes[name].append(name)
                for _, fish_types in self.bot.fish.items():
                    for fish_type, fish_data in fish_types.items():
                        if info[0] == fish_data['raw_name']:
                            move_x.append(random.randint(min_max_x[tank_info][0], min_max_x[tank_info][1]))
                            fish_y_value.append(random.randint(min_max_y[tank_info][0], min_max_y[tank_info][1]))
                            fish_selections.append(f"C:/Users/JT/Pictures/Aqua{fish_data['image'][1:16]}{golden_inverted_normal}_fish_size{fish_data['image'][20:]}")



            # gif variables
            file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
            gif_filename = f'{file_prefix}/gifs/actual_gifs/user_tank{gif_name}.gif'

            # Open our constant images
            tank_theme = tank_row[0]['tank_theme'][tank_slot]
            background = Image.open(f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}.png")
            midground = Image.open(f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}_midground.png")
            foreground = Image.open(f"{file_prefix}/background/{tank_types[tank_info]}.png")
            for x in range(0, len(fish_selections)):
                im.append(Image.open(fish_selections[x]))
            # For each frame of the gif...
            for _ in range(60):

                # Add a fish to the background image
                this_background = background.copy()
                # adds multiple fish and a midground if its a fishbowl
                for x in range(0, len(im)):
                    this_background.paste(im[x], (move_x[x], fish_y_value[x]), im[x])
                    move_x[x] += fish_size_speed[tank_info]
                    if move_x[x] > min_max_x[tank_info][1]:
                        move_x[x] = min_max_x[tank_info][0]
                this_background.paste(midground, (0, 0), midground)
                this_background.paste(foreground, (0, 0), foreground)

                # Save the generated image to memory
                f = io.BytesIO()
                this_background.save(f, format="PNG")
                f.seek(0)
                files.append(f)

                # Move fish

            # Save the image sequence to a gif
            image_handles = [imageio.imread(i) for i in files]
            imageio.mimsave(gif_filename, image_handles)

            # Close all our file handles because oh no
            for i in files:
                i.close()

        # Send gif to Discord
        await ctx.send(file=discord.File(gif_filename))

def setup(bot):
    bot.add_cog(Aquarium(bot))
