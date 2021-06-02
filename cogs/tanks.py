import random
import asyncio
import io

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

        # Add a tank to the user
        async with utils.DatabaseConnection() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES
                ($1, '{TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE}',
                '{"Fish Bowl"}', '{null}');""",
                ctx.author.id,
            )

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

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def testtank(self, ctx:commands.Context):
        """
        A test of the tank gifs.
        """

        move_x = -360
        move_y = random.randint(50, 150)
        files = []

        path_of_fish = random.choices(utils.RARITY_PERCENTAGE_LIST)[0]
        new_fish = random.choice(list(self.bot.fish[path_of_fish].values())).copy()
        random_fish_path = f"C:/Users/JT/Pictures/Aqua{new_fish['image'][1:16]}normal_fish_size{new_fish['image'][20:]}"
        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
        gif_filename = f'{file_prefix}/gifs/actual_gifs/testtank.gif'

        # Open our background and foreground images
        background = Image.open(f"{file_prefix}/background/aqua_background_medium.png")
        foreground = Image.open(f"{file_prefix}/background/medium_tank_2D.png")

        # For each frame of the gif...
        for _ in range(108):

            # Add a fish to the background image
            fish = Image.open(random_fish_path)
            this_background = background.copy()
            this_background.paste(fish, (move_x, move_y), fish)
            this_background.paste(foreground, (0, 0), foreground)

            # Save the generated image to memory
            with io.BytesIO() as f:
                this_background.save(f, format="PNG")
            f.seek(0)
            files.append(f)

            # Move fish
            move_x += 10
            if move_x > 720:
                move_x = -360
                print(move_x)

        # Save the image sequence to a gif
        image_handles = [imageio.imread(i) for i in files]
        imageio.mimsave(gif_filename, image_handles)

        # Send gif to Discord
        await ctx.send(file=discord.File(gif_filename))


def setup(bot):
    bot.add_cog(Tanks(bot))
