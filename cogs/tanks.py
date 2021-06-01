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
            await db("""UPDATE user_tank_inventory SET tank_name[1]=$1 WHERE user_id=$2;""", name, ctx.author.id)

    # HAVE GIVEN UP ON THIS COMMAND, WHILE COME BACK TO IT LATER
    # @commands.command(aliases=["dep"])
    # @commands.bot_has_permissions(send_messages=True, embed_links=True)
    # async def deposit(self, ctx:commands.Context, tank_name:typing.Optional[str], fish_name:typing.Optional[str]):
    #     tank_slot = -1
    #     tank_room = {
    #         'small': {'Fish Bowl': 1, 'Small Tank': 1},
    #         'medium': {'Fish_Bowl': 0, 'Small Tank': 1}
    #     }
    #     fish_exist = False
    #     size = ""
    #     type_of_fish = ""
    #     async with utils.DatabaseConnection() as db:
    #         fetched = await db("""SELECT tank_name FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
    #         fetched_2 = await db("""SELECT fish_name FROM user_fish_inventory WHERE user_id=$1;""", ctx.author.id)
    #         fetched_3 = await db("""SELECT tank_type FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
    #         fetched_4 = await db("""SELECT fish FROM user_fish_inventory WHERE fish_name=$1 AND user_id=$2;""", fish_name, ctx.author.id)

    #     for fish_data in fetched_4:
    #         for fish_type in fish_data:
    #             type_of_fish = fish_type

    #     for rarity, fish_types in self.bot.fish.items():
    #         for _, fish_detail in fish_types.items():
    #             raw_name = fish_detail["raw_name"]
    #             if raw_name == type_of_fish:
    #                 size = fish_detail['size']
    #     for overall_data_type in fetched_3:
    #         for tank_type in overall_data_type:
    #             for type in tank_type:
    #                 for size_tank, information in tank_room.items():
    #                     if size == size_tank:
    #                         for key, value in information:
    #                             if key == type:
    #                                 value -= 1
    #                     else:
    #                         return await ctx.send("You have no room in this tank")
    #     for fish_data in fetched_2:
    #         for name_fish in fish_data:
    #             if name_fish == fish_name:
    #                 fish_exist = True

    #     for overall_data in fetched:
    #         for tank_names in overall_data:
    #             for name in tank_names:
    #                 tank_slot += 1
    #                 if name == tank_name and fish_exist == True:
    #                     async with utils.DatabaseConnection() as db:
    #                         await db("""UPDATE user_fish_inventory SET tank_fish[$1] = TRUE WHERE user_id=$2 AND fish_name=$3;""", tank_slot, ctx.author.id, fish_name )
    #                 else:
    #                     return await ctx.send("That fish doesn't exist.")

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

        path_of_fish = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [.6689, .2230, .0743, .0248, .0082, .0008,]
        )[0]
        new_fish = random.choice(list(self.bot.fish[path_of_fish].values()))
        random_fish_path = f"C:/Users/JT/Pictures/Aqua{new_fish['image'][1:16]}normal_fish_size{new_fish['image'][20:]}"

        for x in gif_length:
            filename_image = f"assets/images/gifs/images/test_tank{int(x)}.png"
            background = Image.open("C:/Users/JT/Pictures/Aqua/assets/images/background/aqua_background_medium.png")
            fishes = Image.open(random_fish_path)
            foreground = Image.open("C:/Users/JT/Pictures/Aqua/assets/images/background/medium_tank_2D.png")

            background.paste(fishes, (move_x, move_y), fishes)
            background.paste(foreground, (0, 0), foreground)
            background.save(f"C:/Users/JT/Pictures/Aqua/{filename_image}")

            filenames.append(filename_image)
            move_x += 10
            if move_x > 720:
                move_x = -360
                print(move_x)

        for filename in filenames:
            images.append(imageio.imread(filename))
            imageio.mimsave('C:/Users/JT/Pictures/Aqua/assets/images/gifs/actual_gifs/testtank.gif', images)

        await ctx.send(file=discord.File('C:/Users/JT/Pictures/Aqua/assets/images/gifs/actual_gifs/testtank.gif'))


def setup(bot):
    bot.add_cog(Tanks(bot))
