import discord
import random
import math

# Does all the xp stuff
async def xp_finder_adder(self, user: discord.User, played_with_fish):
    # ranges of how much will be added
    total_xp_to_add = random.randint(1, 25)

    # initial acquired fish data
    async with self.bot.database() as db:
        fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                    
    # level increase xp calculator
    xp_per_level = math.floor(25 * fish_rows[0]['fish_level'] ** 1.5)
    
    # for each tick of xp...
    for i in range(total_xp_to_add):

        # if the xp is higher or equal to the xp recquired to level up...
        if fish_rows[0]['fish_xp'] >= fish_rows[0]['fish_xp_max']:

            # update the level to increase by one, reset fish xp, and set fish xp max to the next level xp needed
            async with self.bot.database() as db:
                await db("""UPDATE user_fish_inventory SET fish_level = fish_level + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                await db("""UPDATE user_fish_inventory SET fish_xp = 0 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                await db("""UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""", int(xp_per_level), user.id, played_with_fish)
        
        # adds one xp regets new fish_rows
        async with self.bot.database() as db:
            await db("""UPDATE user_fish_inventory SET fish_xp = fish_xp + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)

    return total_xp_to_add

def get_fixed_field(field):
    """
    Return a list of tuples for the rarity-level in the pagination to fix fields that are too large
    """
    fish_string_split = field[1].split('\n')
    fixed_field = []
    current_string = ""
    fish_character_sum = 0

    for index, fish_string in enumerate(fish_string_split):
        fish_character_sum += len("\n" + fish_string)
        if fish_character_sum < 1020:
            current_string += "\n" + fish_string
            if index == len(fish_string_split) - 1:
                fixed_field.append((field[0], current_string))
        else:
            fixed_field.append((field[0], current_string))
            current_string = fish_string
            fish_character_sum = 0
        
    if not fixed_field:
        fixed_field = [field]

    return fixed_field

def create_bucket_embed(user, field):
    """
    Creates the embed for the pagination page for the fishbucket
    """
    embed = discord.Embed()  # Create a new embed to edit the message
    embed.title = f"**{user.display_name}'s Fish Bucket**\n"
    embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
    return embed

# def create_info_embed(field):
#     embed = discord.Embed()  # Create a new embed to edit the message
#     embed.title = "Commands (anything in quotes is a variable, and the quotes may or may not be needed)"
#     embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
#     return embed
        
def seconds_converter(time):
    if 5_400 > time >= 3_600:
        form = 'hour'
        time /= 60 * 60
    elif time > 3_600:
        form = 'hours'
        time /= 60 * 60
    elif 90 > time >= 60:
        form = 'minute'
        time /= 60
    elif time >= 60:
        form = 'minutes'
        time /= 60
    elif time < 1.5:
        form = 'second'
    else:
        form = 'seconds'
    return f"{round(time)} {form}"