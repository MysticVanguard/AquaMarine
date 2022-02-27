import math
import asyncio
import typing
from cogs import utils

import discord
from discord.ext import vbu

# Finds out what level and xp each fish will be


async def xp_finder_adder(
    user: typing.Union[discord.User, discord.Member],
    played_with_fish: str,
    xp_per_fish: int,
    level: bool,
) -> None:
    """
    Takes umm it takes the uh so it takes the it's called every time every fish in a tank and it takes every
    it it takes the xp for that uh that fish and uh um and then basically it stop i hate it
    and then so it so it it gets the new uh it gets the new fish rows data and it's like
    it sets the current xp to um uh the current xp plus the new xp added and it sets xp needed to the fish xp that
    it got from the data and then added level is zero

    Add to the fish's xp and level.
    """

    # Intial data for fish
    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
            user.id,
            played_with_fish,
        )

    # Update what the current xp will be
    current_xp = fish_rows[0]["fish_xp"] + xp_per_fish

    # Find out the xp needed from the data
    xp_needed = fish_rows[0]["fish_xp_max"]

    # Initiate how many levels added as 0
    added_level = 0

    # If the fish triggered the bonus level from amazement upgrade add a level
    if level is True:
        added_level += 1

    # Adds a level as long as the current xp is bigger than the xp needed, refinding xp needed and resetting current xp
    async with vbu.Database() as db:

        # While the fish has more xp after the entertain than the xp needed...
        while current_xp >= xp_needed:

            # Increase the level
            inventory_rows = await db(
                """UPDATE user_fish_inventory SET fish_level = fish_level + $3 WHERE
                user_id = $1 AND fish_name = $2 RETURNING fish_level""",
                user.id,
                played_with_fish,
                (1 + added_level),
            )

            # Calculate the current xp by subtracting the xp needed for the last level from the old xp
            current_xp = current_xp - xp_needed

            # Calculate the next level using the fish's current level (and the added level if that was hit)
            xp_needed = math.floor(
                25 * (inventory_rows[0]["fish_level"] + added_level) ** 1.5
            )

        # Once the fish is done leveling set the current xp and the xp needed to their appropriate values
        await db(
            """UPDATE user_fish_inventory SET fish_xp = $3 WHERE user_id = $1 AND fish_name = $2""",
            user.id,
            played_with_fish,
            current_xp,
        )
        await db(
            """UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""",
            xp_needed,
            user.id,
            played_with_fish,
        )


# This is used to fix fields that are too long (i.e. If someone has too many of one rarity in their fish bucket)


def get_fixed_field(field):
    """
    Return a list of tuples for the rarity-level in the pagination to fix fields that are too large
    """

    # This gets the main part of the field that will be put into an embed in a list of each time new line is given
    fish_string_split = field[1].split("\n")

    # Initializes the fixed field list, current string string, and fish char sum
    fixed_field = []
    current_string = ""
    fish_character_sum = 0

    # For each new line segment. The part of a bucket that says:
    # "Red": Red Betta (Size: Small, Alive: True)
    for index, fish_string in enumerate(fish_string_split):

        # Find the length of that piece with the new line
        fish_character_sum += len("\n" + fish_string)

        # If it gets to a point where the sum is less than 1020...
        if fish_character_sum < 1020:

            # Add the current string and new line to "current string"
            current_string += "\n" + fish_string
            # If it's the last string in the field...
            if index == len(fish_string_split) - 1:

                # Add it to the new field with the original starting part
                fixed_field.append((field[0], current_string))

        # Else if it's greater...
        else:

            # Add it to the new field with the original starting part
            fixed_field.append((field[0], current_string))
            # Set the current string to "current string"
            current_string = "\n" + fish_string
            # Set the sum back to 0
            fish_character_sum = len("\n" + fish_string)

    # If there was nothing sent to fixed field...
    if not fixed_field:

        # Simply don't change the field and send it back
        fixed_field = [field]

    # Send the fixed field
    return fixed_field


# Puts together an embed based on the field given


def create_bucket_embed(
    user, field: tuple[str, str], page: int, custom_title: str = None,
):
    """
    Creates the embed for the pagination page for the fishbucket
    """

    # Creates a new embed
    embed = discord.Embed()

    # Sets the title to the custom title or just "user's fish bucket"
    embed.title = custom_title or f"**{user.display_name}'s Fish Bucket**\n"

    # Sets the name of the field to the first part of the given field, then the value to the second part
    embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
    embed.set_footer(text=f"Page {page}")

    # Returns the field
    return embed


# This takes in the ctx, all of the fields for the embed, the user, and the custom title


async def paginate(ctx, fields, user, custom_str=None):

    # intiiates bot as ctx.bot
    bot = ctx.bot
    # Sets the current index to 1
    curr_index = 1
    # Sets the current field to be the first field
    curr_field = fields[curr_index - 1]
    # Creates the first embed
    embed = create_bucket_embed(user, curr_field, curr_index, custom_str)

    # Set up the buttons for pagination
    left = discord.ui.Button(
        custom_id="left", emoji="◀️", style=discord.ui.ButtonStyle.primary
    )
    right = discord.ui.Button(
        custom_id="right", emoji="▶️", style=discord.ui.ButtonStyle.primary
    )
    stop = discord.ui.Button(
        custom_id="stop", emoji="⏹️", style=discord.ui.ButtonStyle.danger
    )
    numbers = discord.ui.Button(
        custom_id="numbers", emoji="🔢", style=discord.ui.ButtonStyle.primary
    )

    # Set up the valid buttons to be the first 3 always
    valid_buttons = [left, right, stop]
    # Then if theres more than one page, add numbers
    if len(fields) > 1:
        valid_buttons.append(numbers)

    # Put the buttons together
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(*valid_buttons)
    )

    # Send the message
    fish_message = await ctx.send(embed=embed, components=components)

    # Check to see if the button is...
    def button_check(payload):

        # The correct message
        if payload.message.id != fish_message.id:
            return False
        # The correct button
        if payload.component.custom_id in [
            left.custom_id,
            right.custom_id,
            stop.custom_id,
            numbers.custom_id,
        ]:
            bot.loop.create_task(payload.response.defer_update())
        # The correct user
        return payload.user.id == ctx.author.id

    while True:  # Keep paginating until the user clicks stop

        # Check to see if they...
        try:

            # Click a button, it works with the button check, and it doesnt time out
            chosen_button_payload = await bot.wait_for(
                "component_interaction", timeout=60.0, check=button_check
            )
            # Set the chosen button to be the id
            chosen_button = chosen_button_payload.component.custom_id.lower()

        # If it times out...
        except asyncio.TimeoutError:

            # The chosen button is set to stop
            chosen_button = "stop"

        # A dict that sets left to be one to the left of the current field, and right to be one to the right of it,
        # but not go too far left or right
        index_chooser = {
            "left": max(1, curr_index - 1),
            "right": min(len(fields), curr_index + 1),
        }

        # If the button is left or right...
        if chosen_button in index_chooser.keys():

            # Set the index to be the correct in bounds index
            curr_index = index_chooser[chosen_button]
            # Set the field to be the corresponding field
            curr_field = fields[curr_index - 1]
            # Edit the embed with the new page
            await fish_message.edit(
                embed=create_bucket_embed(
                    user, curr_field, curr_index, custom_str)
            )

        # If the button is stop...
        elif chosen_button == "stop":

            # Disable all the components
            await fish_message.edit(components=components.disable_components())
            # End the while loop
            break

        # If the button is numbers and theres more than one field...
        elif chosen_button == "numbers" and len(fields) > 1:

            # Ask the user what page they want to go to
            pages_string = f"go to? (1-{len(fields)})"
            page_selected = await utils.create_select_menu(bot, ctx, range(1, len(fields)+1), "page", pages_string)

            user_input = int(page_selected)

            # Set the current index to be the one the user says
            curr_index = min(len(fields), max(1, user_input))
            # Set the field to the corresponding one
            curr_field = fields[curr_index - 1]

            # Edit the message with the new field
            await fish_message.edit(
                embed=create_bucket_embed(user, curr_field, custom_str)
            )
