import asyncio
from cogs import utils
import discord
from discord.ext import vbu

# Finds out what level and xp each fish will be


# Dict of all the tank types
tank_types = {
    "Fish Bowl": "fishbowl",
    "Small Tank": "Small_Tank_2D",
    "Medium Tank": "Medium_Tank_2D",
}

file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"

EMOJIS = {
    "achievement_star": "<:achievement_star:877646167087906816>",
    "achievement_star_new": "<:achievement_star_new:877737712046702592>",
    "achievement_star_no": "<:achievement_star_no:877646167222141008>",
    "amfc": "<:AMFC:913680729177751563>",
    "aqua_blep": "<:AquaBlep:878248090400870401>",
    "aqua_bonk": "<:AquaBonk:877722771935883265>",
    "aqua_cool": "<:AquaCool:878248090895802438>",
    "aqua_fish": "<:AquaFish:877939115948134442>",
    "aqua_love": "<:AquaLove:878248091201982524>",
    "aqua_pensive": "<:AquaPensive:877939116266909756>",
    "aqua_scared": "<:AquaScared:877939115943936074>",
    "aqua_shrug": "<:AquaShrug:877939116480802896>",
    "aqua_unamused": "<:AquaUnamused:877939116132696085>",
    "aqua_smile": "<:AquaSmile:877939115994255383>",
    "aqua_clean": "<:AquaClean:965778951605714994>",
    "aqua_craft": "<:AquaCraft:965778951773503569>",
    "aqua_eat": "<:AquaEat:965778952121647215>",
    "aqua_eyes": "<:AquaEyes:965778952083869707>",
    "aqua_rich": "<:AquaRich:965778951937097748>",
    "aqua_stare": "<:AquaStare:965778951643492382>",
    "aqua_tank": "<:AquaTank:965778951576354877>",
    "aqua_tap": "<a:AquaTap:965778952029339658>",
    "aqua_trash": "<:AquaTrash:965778950980796427>",
    "bar_1": "<:bar_1:877646167184408617>",
    "bar_2": "<:bar_2:877646166823694437>",
    "bar_3": "<:bar_3:877646167138267216>",
    "bar_e": "<:bar_e:877646167146643556>",
    "bar_empty": "<:__:886381017051586580>",
    "bar_L": "<:bar_L:886377903615528971>",
    "bar_L_branch": "<:bar_L_branch:886377903581986848>",
    "bar_L_straight": "<:bar_L_straight:886379040884260884>",
    "bar_R": "<:bar_R:877646167113080842>",
    "branch": "<:branch:886377903825252402>",
    "casts": "<:Casts:911465713938612235>",
    "common_fish_bag": "<:common_fish_bag:877646166983053383>",
    "doubloon": "<:doubloon:878297091057807400>",
    "experience_potion": "<:experience_potion:911465714412568616>",
    "feeding_potion": "<:feeding_potion:911465714379018261>",
    "fish_flake": "<:fish_flakes:877646167188602880>",
    "fish_pellet": "<:fish_pellets:911465714412552212>",
    "fish_points": "<:fish_points:911468089420427324>",
    "fish_wafer": "<:fish_wafers:911465714395799574>",
    "gfu": "<:GFU:913680729517469716>",
    "high_level_fish_bag": "<:high_level_fish_bag:912057609496985690>",
    "inverted_fish_bag": "<:inverted_fish_bag:912057608863637545>",
    "keep": "<:keep:844594468580491264>",
    "mutation_potion": "<:mutation_potion:911465714420949072>",
    "rare_fish_bag": "<:rare_fish_bag:877646167121489930>",
    "revival": "<:revival:878297091158474793>",
    "roll": "<a:roll:886068357378502717>",
    "sand_dollar": "<:sand_dollar:877646167494762586>",
    "sand_dollar_pile": "<:sand_dollar_pile:925288312611172372>",
    "sand_dollar_stack": "<:sand_dollar_stack:925288312418209853>",
    "sell": "<:sell:844594478392147968>",
    "straight": "<:straight:886377903879753728>",
    "straight_branch": "<:straight_branch:886377903837806602>",
    "uncommon_fish_bag": "<:uncommon_fish_bag:877646167146651768>",
    "pile_of_bottle_caps": "<:pile_of_bottle_caps:934600170274951188>",
    "plastic_bottle": "<:plastic_bottle:934600322305912904>",
    "plastic_bag": "<:plastic_bag:934600170228817930>",
    "seaweed_scraps": "<:seaweed_scraps:982769507095445544>",
    "broken_fishing_net": "<:broken_fishing_net:934600170346283038>",
    "halfeaten_flip_flop": "<:halfeaten_flipflop:934600169834577921>",
    "pile_of_straws": "<:pile_of_straws:934600169872306227>",
    "old_boot": "<:old_boot:934600170161717360>",
    "old_tire": "<:old_tire:934600169918439446>",
    "fishing_boots": "<:fishing_boots:982769507212873728>",
    "trash_toys": "<:trash_toys:982769507070255224>",
    "super_food": "<:AquaSmile:877939115994255383>",
    "new_location_unlock": "<:AquaShrug:877939116480802896>",
}

# The different acceptable names for items bought in the shop
COMMON_BAG_NAMES = ["Common Fish Bag", "Common", "Cfb"]
UNCOMMON_BAG_NAMES = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
RARE_BAG_NAMES = ["Rare Fish Bag", "Rare", "Rfb"]
INVERTED_BAG_NAMES = ["Inverted Fish Bag", "Inverted", "Ifb"]
HIGH_LEVEL_BAG_NAMES = ["High Level Fish Bag", "High Level", "Hlfb"]
FISH_FLAKES_NAMES = ["Fish Flakes", "Flakes", "Ff"]
FISH_BOWL_NAMES = ["Fish Bowl", "Bowl", "Fb"]
SMALL_TANK_NAMES = ["Small Tank", "Small", "St"]
MEDIUM_TANK_NAMES = ["Medium Tank", "Medium", "Mt"]
PLANT_LIFE_NAMES = ["Plant Life", "Plant", "Pl"]
FISH_REVIVAL_NAMES = ["Fish Revival", "Revival", "Fr"]
CASTS_NAMES = ["Fishing Casts", "Casts", "Fc"]
SAND_DOLLAR_NAMES = ["Sand Dollars", "Dollars", "Sd"]
FISH_PELLETS_NAMES = ["Fish Pellets", "Pellets", "Fp"]
FISH_WAFERS_NAMES = ["Fish Wafers", "Wafers", "Fw"]
FISH_POINTS_NAMES = ["Fish Points", "Points", "P"]
EXPERIENCE_POTION_NAMES = ["Experience Potion", "Experience", "E"]
MUTATION_POTION_NAMES = ["Mutation Potion", "Mutation", "M"]
FEEDING_POTION_NAMES = ["Feeding Potion", "Feeding", "F"]
NEW_LOCATION_UNLOCK_NAMES = ["New Location Unlock", "Unlock", "NLU"]


# List of names for tank themes
TANK_THEMES = PLANT_LIFE_NAMES

# Daylight savings variable because for some reason i need to
# add four and then an hour when its daylight savings,
# will be changed to 4 when daylight savings is over
DAYLIGHT_SAVINGS = 4

# What colors the embed should have based on rarity
RARITY_CULERS = {
    "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
    "uncommon": 0x75FE66,  # Green
    "rare": 0x4AFBEF,  # Blue
    "epic": 0xE379FF,  # Light Purple
    "legendary": 0xFFE80D,  # Gold
    "mythic": 0xFF0090,  # Hot Pink
}

items_required = {
    "Cast": ({"broken_fishing_net": 2},
             "Gives you one cast."),
    "Fish Bag": ({"plastic_bag": 2, "pile_of_straws": 1},
                 "Gives you one fish bag. (Either common, uncommon, or rare)"),
    "Fishing Boots": ({"old_boot": 2, "broken_fishing_net": 3},
                      "Gives you a 5% chance to get 2 casts instead of 1 each hour. (stacks up to 5)"),
    "Trash Toys": ({"old_tire": 2, "halfeaten_flip_flop": 2, "plastic_bottle": 5, "seaweed_scraps": 4},
                   "Gives you a 50% bonus to xp gotten from entertaining. (stacks up to 5)"),
    "Super Food": ({"seaweed_scraps": 4, },
                   "Used to feed all fish in a tank, no matter their level.")
}


async def enough_to_craft(crafted: str, user_id: int):
    for item, required in items_required[crafted][0].items():
        async with vbu.Database() as db:
            amount = await db(f"""SELECT {item} FROM user_item_inventory WHERE user_id = $1""", user_id)
        if amount[0][item] < required:
            return False
    return True

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


async def create_select_menu(bot, ctx, option_list, type_noun, type_verb, remove=False):
    """
    This will create a select menu from the given list,
    have the user select one, and return the selection
    """

    # Initiates the option list
    test_options = []

    # For each name that isnt "" add it as an option for the select menu
    for option in option_list:
        if option != "":
            test_options.append(discord.ui.SelectOption(
                label=option, value=option))

    # Set the select menu with the options
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.SelectMenu(
                custom_id=type_verb,
                options=test_options,
                placeholder="Select an option",
            )
        )
    )

    # Ask them what they want to do with component
    message = await ctx.send(
        f"What {type_noun} would you like to {type_verb}?",
        components=components,
    )

    # If it's the correct message and author return true
    def check(payload):
        if payload.message.id != message.id:
            return False

        # If its the wrong author send an ephemeral message
        if payload.user.id != ctx.author.id:
            bot.loop.create_task(
                payload.response.send_message(
                    "You can't respond to this message!", ephemeral=True
                )
            )
            return False
        return True

    # If it works don't fail, and if it times out say that
    try:
        payload = await bot.wait_for(
            "component_interaction", check=check, timeout=60
        )
        await payload.response.defer_update()
    except asyncio.TimeoutError:
        return await ctx.send(
            f"Timed out asking for {type_noun} to "
            f"{type_verb} <@{ctx.author.id}>"
        )

    # Return what they chose
    if remove == True:
        await message.delete()
    return str(payload.values[0])


async def create_modal(bot, Interaction, title, placeholder):
    """
    Modal
    """

    # Send a modal back to the user
    await Interaction.response.send_modal(
        (sent_modal := discord.ui.Modal(
            title=title,
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        label="Input text label",
                        style=discord.TextStyle.short,
                        placeholder=placeholder,
                        min_length=1,
                        max_length=32,
                    ),
                ),
            ],
        ))
    )

    # Wait for an interaction to be given back
    try:
        interaction: discord.Interaction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.data['custom_id'] == sent_modal.custom_id,
            timeout=60.0
        )
    except asyncio.TimeoutError:
        return None, None

    # Go through the response components and get the first (and only) value from the user
    assert interaction.components
    given_value = interaction.components[0].components[0].value

    # Respond with what the user said
    return given_value, interaction
