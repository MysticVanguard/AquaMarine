import random
import asyncio
import io
import numpy as np

import discord
from discord.ext import commands
from PIL import Image
import imageio

import utils


class Tanks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def firsttank(self, ctx:commands.Context):
        """
        Gives your your first tank.
        """

        # See if they already have a tank
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
        if fetched:
            return await ctx.send("You have your first tank already!")

        type_of_tank = "Fish Bowl"
        # Add a tank to the user
        async with utils.DatabaseConnection() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES ($1);""", ctx.author.id)
            await db(
                """UPDATE user_tank_inventory SET tank[1]=TRUE, tank_type[1]=$2,
                fish_room[1] = 1 WHERE user_id=$1""", ctx.author.id, type_of_tank)

        # Ask the user what they want to name their tank
        def check(message):
            return all([
                message.author == ctx.author,
                message.channel == ctx.channel,
                len(message.content) <= 32,
            ])
        await ctx.send("What do you want to name your first tank? (32 character limit)")
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
        async with utils.DatabaseConnection() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_name[1]=$1 WHERE user_id=$2;""",
                name, ctx.author.id,
            )

    @commands.command(aliases=["dep"])
    @commands.bot_has_permissions(send_messages=True)
    async def deposit(self, ctx:commands.Context, tank_name, fish_deposited):
        '''
        Deposits target fish into target tank
        '''

        # variables for size value and the slot the tank is in
        size_values = {"small": 1, "medium": 5, "large": 10}
        tank_slot = 0

        # fetches the two needed rows from the database
        async with utils.DatabaseConnection() as db:
            fish_row = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", ctx.author.id, fish_deposited)
            tank_row = await db("""SELECT * FROM user_tank_inventory WHERE user_id =$1""", ctx.author.id)

        # all the checks for various reasons the command shouldn't be able to work
        if fish_row[0]['tank_fish']:
            return await ctx.send("This fish is already in a tank!")
        if not fish_row:
            return await ctx.send(f"You have no fish named {fish_deposited}!")
        if not tank_row or tank_row[0]['tank'] == ['False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False', 'False']:
            return await ctx.send(f"You have no tanks!")
        
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

        # if the fish is normal...
        if fish_row[0]['fish_size'] != 'tiny' and fish_row[0]['fish_size'] != 'xl':

            # add the fish to the tank in the database
            async with utils.DatabaseConnection() as db:
                await db(
                    """UPDATE user_tank_inventory SET fish_room[$2] = fish_room[$2] - $3 WHERE user_id=$1""", ctx.author.id, tank_slot, int(size_values[fish_row[0]["fish_size"]]))
                await db(
                """UPDATE user_fish_inventory SET tank_fish = $3 WHERE fish_name=$1 AND user_id=$2""", fish_deposited, ctx.author.id, tank_name)
            return await ctx.send("Fish deposited!")
        elif fish_row[0]['fish_size'] == 'tiny':
            async with utils.DatabaseConnection() as db:
                await db(
                    """UPDATE user_tank_inventory SET tiny_fish_room[$2] = tiny_fish_room[$2] - 1 WHERE user_id=$1""", ctx.author.id, tank_slot)
                await db(
                """UPDATE user_fish_inventory SET tank_fish = $3 WHERE fish_name=$1 AND user_id=$2""", fish_deposited, ctx.author.id, tank_name)
            return await ctx.send("Fish deposited!")
        elif fish_row[0]['fish_size'] == 'xl':
            async with utils.DatabaseConnection() as db:
                await db(
                    """UPDATE user_tank_inventory SET xl_fish_room[$2] = xl_fish_room[$2] - 1 WHERE user_id=$1""", ctx.author.id, tank_slot)
                await db(
                """UPDATE user_fish_inventory SET tank_fish = $3 WHERE fish_name=$1 AND user_id=$2""", fish_deposited, ctx.author.id, tank_name)
            return await ctx.send("Fish deposited!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def testtank(self, ctx:commands.Context):
        """
        A test of the tank gifs.
        """
        #Typing Indicator
        async with ctx.typing():
            move_x = -360
            move_y = random.randint(50, 150)
            files = []
            path_of_fish = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]
            new_fish = random.choice(list(self.bot.fish[path_of_fish].values())).copy()
            random_fish_path = f"C:/Users/JT/Pictures/Aqua{new_fish['image'][1:16]}normal_fish_size{new_fish['image'][20:]}"
            file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
            gif_filename = f'{file_prefix}/gifs/actual_gifs/testtank.gif'

            
            # Open our constant images
            background = Image.open(f"{file_prefix}/background/aqua_background_Medium_Tank_2D.png.png")
            foreground = Image.open(f"{file_prefix}/background/medium_tank_2D.png")
            fish = Image.open(random_fish_path)

            # For each frame of the gif...
            for _ in range(108):

                # Add a fish to the background image
                this_background = background.copy()
                this_background.paste(fish, (move_x, move_y), fish)
                this_background.paste(foreground, (0, 0), foreground)

                # Save the generated image to memory
                f = io.BytesIO()
                this_background.save(f, format="PNG")
                f.seek(0)
                files.append(f)

                # Move fish
                move_x += 15
                if move_x > 720:
                    move_x = -360

            # Save the image sequence to a gif
            image_handles = [imageio.imread(i) for i in files]
            imageio.mimsave(gif_filename, image_handles)

            # Close all our file handles because oh no
            for i in files:
                i.close()

        # Send gif to Discord
        await ctx.send(file=discord.File(gif_filename))

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def show(self, ctx:commands.Context, tank_name):
        """
        Shows a users tanks
        """
        #Typing Indicator
        async with ctx.typing():

            # variables
            move_x = []
            min_max_y = {"Fish Bowl": (50, 50), "Small Tank": (15, 200), "Medium Tank": (25, 200)}
            min_max_x = {"Fish Bowl": (-180, 150), "Small Tank": (-180, 360), "Medium Tank": (-180, 720)}
            im = []
            fish_y_value = []
            files = []
            golden_inverted_normal = 'normal'
            fish_selections = []
            gif_name = random.randint(1, 1000)
            tank_types = {"Fish Bowl": "fishbowl", "Small Tank": "Small_Tank_2D", "Medium Tank": "Medium_Tank_2D"}
            tank_slot = 0

            # gets database info for tank
            async with utils.DatabaseConnection() as db:
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
                if "golden" in selected_fish_types['fish']:
                        selected_fish_types['fish'].pop("golden")
                        golden_inverted_normal = 'golden'
                if "inverted" in selected_fish_types['fish']:
                        selected_fish_types['fish'].pop("inverted")
                        golden_inverted_normal = 'inverted'
                for _, fish_types in self.bot.fish.items():
                    for fish_type, fish_data in fish_types.items():
                        if selected_fish_types['fish'] == fish_data['raw_name']:
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
            print(fish_y_value)
            # For each frame of the gif...
            for _ in range(60):

                # Add a fish to the background image
                this_background = background.copy()
                # adds multiple fish and a midground if its a fishbowl
                for x in range(0, len(im)):
                    this_background.paste(im[x], (move_x[x], fish_y_value[x]), im[x])
                    move_x[x] += 15
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
    bot.add_cog(Tanks(bot))
