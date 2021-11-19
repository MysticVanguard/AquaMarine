import random
import asyncio
from datetime import datetime as dt, timedelta
import io
from cogs import utils

from PIL import Image
import imageio
import discord
from discord.ext import commands, vbu

from cogs.utils.fish_handler import DAYLIGHT_SAVINGS


class Aquarium(vbu.Cog):

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def firsttank(self, ctx: commands.Context):
        """
        This command gives the user their first tank.
        """

        # See if they already have a tank
        async with vbu.Database() as db:
            fetched = await db("""SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
        if fetched:
            return await ctx.send("You have your first tank already!")

        # Add a tank to the user
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES ($1);""", ctx.author.id)
            await db(
                """UPDATE user_tank_inventory SET tank[1]=TRUE, tank_type[1]='Fish Bowl',
                fish_room[1] = 1, tank_theme[1] = 'Aqua' WHERE user_id=$1""",
                ctx.author.id,
            )

        # Ask the user what they want to name their tank
        def check(message):
            return all([
                message.author == ctx.author,
                message.channel == ctx.channel,
                message.content,
                len(message.content) <= 32,
                message.content != "none",
            ])
        await ctx.send("What do you want to name your first tank? *(32 character limit and cannot be \"none\")*")
        try:
            name_message = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name_message.content
            await ctx.send(f"You have your new tank, **{name}**!", allowed_mentions=discord.AllowedMentions.none())
        except asyncio.TimeoutError:
            name = "Starter Tank"
            await ctx.send((
                f"Did you forget about me {ctx.author.mention}? I've been waiting for a while "
                f"now! I'll name the tank for you. Let's call it **{name}**."
            ))

        # Save their tank name
        async with vbu.Database() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_name[1]=$1 WHERE user_id=$2;""",
                name, ctx.author.id,
            )

    @vbu.command(aliases=["dep"])
    @commands.bot_has_permissions(send_messages=True)
    async def deposit(self, ctx: commands.Context, *, fish_deposited: str):
        """
        This command deposits a specified fish into a tank.
        """

        # variables for size value and the slot the tank is in
        size_values = {"small": 1, "medium": 5, "large": 10}

        # fetches the two needed rows from the database
        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_deposited)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

        # Creates a select menu of all the tanks and returns the users choice
        tank_name = await utils.create_select_menu(
            self.bot, ctx, tank_row[0]['tank_name'], "tank", "choose")

        # all the checks for various reasons the command shouldn't be able to work
        if not fish_row:
            return await ctx.send(f"You have no fish named **{fish_deposited}**!", allowed_mentions=discord.AllowedMentions.none())
        if not tank_row or True not in tank_row[0]['tank']:
            return await ctx.send("You have no tanks!")
        if tank_name not in tank_row[0]['tank_name']:
            return await ctx.send(f"You have no tank named **{tank_name}**!", allowed_mentions=discord.AllowedMentions.none())
        if fish_row[0]['tank_fish']:
            return await ctx.send("This fish is already in a tank!")
        if fish_row[0]['fish_alive'] is False:
            return await ctx.send("That fish is dead!")

        # finds the tank slot the tank in question is at
        for tank_slot, tank_slot_in in enumerate(tank_row[0]['tank_name']):
            if tank_slot_in == tank_name:
                break
        else:
            return await ctx.send("No tank with that name!")

        # another check
        if tank_row[0]["fish_room"][tank_slot] < size_values[fish_row[0]["fish_size"]]:
            return await ctx.send("You have no room in that tank!")

        # tank slot has one added as python indexes start at 0 but database start at 1
        tank_slot += 1

        # add the fish to the tank in the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_tank_inventory SET fish_room[$2] = fish_room[$2] - $3 WHERE user_id=$1""",
                ctx.author.id, tank_slot, size_values[fish_row[0]
                                                      ["fish_size"]],
            )
            await db(
                """UPDATE user_fish_inventory SET tank_fish = $3, death_time = $4 WHERE fish_name=$1 AND user_id=$2""",
                fish_deposited, ctx.author.id, tank_name, (dt.utcnow(
                ) + timedelta(days=3)),
            )
        relative_time = discord.utils.format_dt(
            dt.utcnow() + timedelta(days=3) - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
        return await ctx.send(f"Fish has been deposited and will die {relative_time}!")

    @vbu.command(aliases=["rem"])
    @commands.bot_has_permissions(send_messages=True)
    async def remove(self, ctx: commands.Context, *, fish_removed: str):
        """
        This command removes a specified fish from a specified tank and has a cooldown.
        """

        # variables for size value and the slot the tank is in
        size_values = {"small": 1, "medium": 5, "large": 10}
        tank_slot = 0

        # fetches the two needed rows from the database
        async with vbu.Database() as db:
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

        # Creates a select menu of all the tanks and returns the users choice
        tank_name = await utils.create_select_menu(
            self.bot, ctx, tank_row[0]['tank_name'], "tank", "choose")

        async with vbu.Database() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_removed, tank_name)

        if not fish_row:
            return await ctx.send(
                f"You have no fish named **{fish_removed}** in that tank!",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        if not tank_row or tank_row[0]['tank'] == ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False']:
            return await ctx.send("You have no tanks!")
        if fish_row[0]['fish_remove_time']:
            if fish_row[0]['fish_remove_time'] + timedelta(days=5) > dt.utcnow():
                time_left = timedelta(
                    seconds=(fish_row[0]['fish_remove_time'] - dt.utcnow()).total_seconds())
                relative_time = discord.utils.format_dt(
                    dt.utcnow() + time_left - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
                return await ctx.send(f"This fish is resting, please try again {relative_time}.")

        # finds the tank slot the tank in question is at
        for tank_slot_in in tank_row[0]['tank_name']:
            if tank_slot_in == tank_name:
                break
            else:
                tank_slot += 1

        # dumb
        tank_slot += 1

        async with vbu.Database() as db:
            await db("""UPDATE user_fish_inventory SET tank_fish = '', death_time = NULL, fish_remove_time = $3 WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_removed, (dt.utcnow() + timedelta(days=5)))
            await db("""UPDATE user_tank_inventory SET fish_room[$3] = fish_room[$3] + $2 WHERE user_id = $1""", ctx.author.id, int(size_values[fish_row[0]['fish_size']]), tank_slot)
        return await ctx.send(
            f"**{fish_removed}** removed from **{tank_name}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def show(self, ctx: commands.Context, *, tank_name: str):
        """
        This command produces a gif of the specified tank. DO NOT USE SLASH COMMANDS
        """

        # Typing Indicator
        async with ctx.typing():

            # variables
            move_x = []
            min_max_y = {"Fish Bowl": (20, 50), "Small Tank": (
                15, 200), "Medium Tank": (20, 200)}
            min_max_x = {
                "Fish Bowl": (-180, 150), "Small Tank": (-180, 360), "Medium Tank": (-800, 720)}
            fish_size_speed = {'Fish Bowl': 17,
                               'Small Tank': 18, 'Medium Tank': 25}
            im = []
            fishes = {}
            fish_y_value = []
            files = []
            dead_alive = []
            golden_inverted_normal = 'normal'
            fish_selections = []
            gif_name = random.randint(1, 1000)
            tank_types = {"Fish Bowl": "fishbowl",
                          "Small Tank": "Small_Tank_2D", "Medium Tank": "Medium_Tank_2D"}
            tank_slot = 0

            # gets database info for tank
            async with vbu.Database() as db:
                selected_fish = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""", ctx.author.id, tank_name)
                tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

            # Check if the tank exists
            if not tank_row:
                return await ctx.send("You have no tanks! use the `firsttank` command to get one!")
            # finds the tank slot
            for tank_slot_in in tank_row[0]['tank_name']:
                if tank_slot_in == tank_name:
                    break
                else:
                    tank_slot += 1
            # finds the type of tank it is and checks if it exists
            if tank_name not in tank_row[0]['tank_name']:
                return await ctx.send(
                    f"You have no tank named **{tank_name}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            tank_info = tank_row[0]['tank_type'][tank_slot]

            # finds what type of fish it is, then adds the paths to a list, as well as finding the fish's random starting position
            for selected_fish_types in selected_fish:
                fishes[selected_fish_types['fish']] = [
                    selected_fish_types['fish_alive']]
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
                    for fish_data in fish_types.values():
                        if info[1] == fish_data['raw_name']:
                            move_x.append(random.randint(
                                min_max_x[tank_info][0], min_max_x[tank_info][1]))
                            fish_y_value.append(random.randint(
                                min_max_y[tank_info][0], min_max_y[tank_info][1]))
                            fish_selections.append(
                                f"C:/Users/JT/Pictures/Aqua/assets/images/{golden_inverted_normal}_fish_size{fish_data['image'][44:]}")
                            if info[0] is True:
                                dead_alive.append(True)
                            else:
                                dead_alive.append(False)

            # gif variables
            file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
            gif_filename = f'{file_prefix}/gifs/actual_gifs/user_tank{gif_name}.gif'

            # Open our constant images
            tank_theme = tank_row[0]['tank_theme'][tank_slot]
            background = Image.open(
                f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}.png")
            midground = Image.open(
                f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}_midground.png")
            foreground = Image.open(
                f"{file_prefix}/background/{tank_types[tank_info]}.png")
            for x in range(0, len(fish_selections)):
                im.append(Image.open(fish_selections[x]).convert("RGBA"))

            # For each frame of the gif...
            for _ in range(60):

                # Add a fish to the background image
                this_background = background.copy()

                # adds multiple fish and a midground if its a fishbowl
                for x in range(0, len(im)):
                    if dead_alive[x] is False:
                        this_background.paste(im[x].rotate(
                            180), (move_x[x], fish_y_value[x]), im[x].rotate(180))
                    else:
                        this_background.paste(
                            im[x], (move_x[x], fish_y_value[x]), im[x])
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
                ...

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
