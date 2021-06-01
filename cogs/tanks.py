import random
import asyncio

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

        gif_length = [str(i) for i in range(1, 109)]
        move_x = -360
        move_y = random.randint(50, 150)
        filenames = []
        images = []

        path_of_fish = random.choices(utils.RARITY_PERCENTAGE_LIST)[0]
        new_fish = random.choice(list(self.bot.fish[path_of_fish].values()))
        random_fish_path = f"C:/Users/JT/Pictures/Aqua{new_fish['image'][1:16]}normal_fish_size{new_fish['image'][20:]}"
        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"

        for x in gif_length:
            filename_image = f"/gifs/images/test_tank{int(x)}.png"
            background = Image.open(f"{file_prefix}/background/aqua_background_medium.png")
            fishes = Image.open(random_fish_path)
            foreground = Image.open(f"{file_prefix}/background/medium_tank_2D.png")

            background.paste(fishes, (move_x, move_y), fishes)
            background.paste(foreground, (0, 0), foreground)
            background.save(f"{file_prefix}{filename_image}")

            filenames.append(filename_image)
            move_x += 10
            if move_x > 720:
                move_x = -360
                print(move_x)

        for filename in filenames:
            images.append(imageio.imread(filename))
            imageio.mimsave(f'{file_prefix}/gifs/actual_gifs/testtank.gif', images)

        await ctx.send(file=discord.File(f'{file_prefix}/gifs/actual_gifs/testtank.gif'))


def setup(bot):
    bot.add_cog(Tanks(bot))
