import discord
import utils
import random
import asyncio
import os
import glob
from os import path
from PIL import Image
import imageio
from discord.ext import commands

class tanks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def firsttank(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
        if fetched:
            return await ctx.send(f"You have your first tank already!")
        else: 
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_tank_inventory VALUES ($1, '{TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE}', '{"Fish Bowl"}', '{null}');""", ctx.author.id)
        await ctx.send("What do you want to name your first tank? (32 character limit)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32

        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"You have your new tank, **{name}**!")
        
        except asyncio.TimeoutError:
            name = "Starter Tank"
            return await ctx.send(f"Did you forget about me {ctx.author.mention}? I've been waiting for a while now! I'll name the tank for you. Let's call it **{name}**")
        
        finally:
            async with utils.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank_name[1] = $1 WHERE user_id = $2;""", name, ctx.author.id)
    
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
        gif_length = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',' 25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61',' 62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '104', '105', '106', '107', '108']
        move_x = -360
        move_y = random.randint(50, 150)
        filenames = []
        images = []

        path_of_fish = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [.6689, .2230, .0743, .0248, .0082, .0008,])[0]
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
    bot.add_cog(tanks(bot))