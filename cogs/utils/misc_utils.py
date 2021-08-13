import discord
import random
import math
import asyncio
import voxelbotutils as vbu


# Does all the xp stuff
async def xp_finder_adder(bot, user: discord.User, played_with_fish):
    # ranges of how much will be added
    total_xp_to_add = random.randint(1, 25)

    # initial acquired fish data
    async with bot.database() as db:
        fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)

    # level increase xp calculator
    xp_per_level = math.floor(25 * fish_rows[0]['fish_level'] ** 1.5)

    # for each tick of xp...
    for i in range(total_xp_to_add):

        # if the xp is higher or equal to the xp recquired to level up...
        if fish_rows[0]['fish_xp'] >= fish_rows[0]['fish_xp_max']:

            # update the level to increase by one, reset fish xp, and set fish xp max to the next level xp needed
            async with bot.database() as db:
                await db("""UPDATE user_fish_inventory SET fish_level = fish_level + 1 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                await db("""UPDATE user_fish_inventory SET fish_xp = 0 WHERE user_id = $1 AND fish_name = $2""", user.id, played_with_fish)
                await db("""UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""", int(xp_per_level), user.id, played_with_fish)

        # adds one xp regets new fish_rows
        async with bot.database() as db:
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


def create_bucket_embed(user, field, custom_title=None):
    """
    Creates the embed for the pagination page for the fishbucket
    """
    embed = discord.Embed()  # Create a new embed to edit the message
    embed.title = custom_title or f"**{user.display_name}'s Fish Bucket**\n"
    embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
    return embed


# def create_info_embed(field):
#     embed = discord.Embed()  # Create a new embed to edit the message
#     embed.title = "Commands (anything in quotes is a variable, and the quotes may or may not be needed)"
#     embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
#     return embed


async def paginate(ctx, fields, user, custom_str=None):
    bot = ctx.bot
    curr_index = 1
    curr_field = fields[curr_index - 1]
    embed = create_bucket_embed(user, curr_field, custom_str)

    # Set up the buttons
    left = vbu.Button(custom_id="left", emoji="◀️", style=vbu.ButtonStyle.PRIMARY)
    right = vbu.Button(custom_id="right", emoji="▶️", style=vbu.ButtonStyle.PRIMARY)
    stop = vbu.Button(custom_id="stop", emoji="⏹️", style=vbu.ButtonStyle.DANGER)
    numbers = vbu.Button(custom_id="numbers", emoji="🔢", style=vbu.ButtonStyle.PRIMARY)

    valid_buttons = [left, right, stop]
    if len(fields) > 1:
        valid_buttons.append(numbers)

    # Put the buttons together
    components = vbu.MessageComponents(
        vbu.ActionRow(*valid_buttons)
    )

    fish_message = await ctx.send(embed=embed, components=components)

    def button_check(payload):

        if payload.message.id != fish_message.id:
            return False

        if payload.component.custom_id in [left.custom_id, right.custom_id, stop.custom_id, numbers.custom_id]:
            bot.loop.create_task(payload.ack())

        return payload.user.id == ctx.author.id

    while True:  # Keep paginating until the user clicks stop
        try:
            chosen_button_payload = await bot.wait_for('component_interaction', timeout=60.0, check=button_check)
            chosen_button = chosen_button_payload.component.custom_id.lower()
        except asyncio.TimeoutError:
            chosen_button = "stop"

        index_chooser = {
            'left': max(1, curr_index - 1),
            'right': min(len(fields), curr_index + 1)
        }

        if chosen_button in index_chooser.keys():
            curr_index = index_chooser[chosen_button]  # Keep the index in bounds
            curr_field = fields[curr_index - 1]

            await fish_message.edit(embed=create_bucket_embed(user, curr_field, custom_str))

        elif chosen_button == "stop":
            await fish_message.edit(components=components.disable_components())
            break  # End the while loop

        elif chosen_button == "numbers" and len(fields) > 1:
            number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")

            # Check for custom message
            def message_check(message):
                return message.author == ctx.author and message.channel == fish_message.channel and message.content.isdigit()

            user_message = await bot.wait_for('message', check=message_check)
            user_input = int(user_message.content)

            curr_index = min(len(fields), max(1, user_input))
            curr_field = fields[curr_index - 1]

            await fish_message.edit(embed=create_bucket_embed(user, curr_field, custom_str))
            await number_message.delete()
            await user_message.delete()


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
