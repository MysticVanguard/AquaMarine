import asyncio
import random
from datetime import datetime as dt, timedelta
import discord
from discord.ext import vbu
from cogs import utils
import math
from PIL import Image
import imageio
import io

FISH_FEED_COOLDOWN = timedelta(hours=6)

min_max_y = {
    "Fish Bowl": (20, 50),
    "Small Tank": (15, 200),
    "Medium Tank": (20, 200),
}
min_max_x = {
    "Fish Bowl": (-180, 150),
    "Small Tank": (-180, 360),
    "Medium Tank": (-800, 720),
}


async def xp_finder_adder(
    user_id: int,
    played_with_fish: str,
    xp_per_fish: int,
    level: bool,
) -> None:
    """
    Add to the fish's xp and level.
    """

    # Intial data for fish
    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
            user_id,
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
                user_id,
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
            user_id,
            played_with_fish,
            current_xp,
        )
        await db(
            """UPDATE user_fish_inventory SET fish_xp_max = $1 WHERE user_id = $2 AND fish_name = $3""",
            xp_needed,
            user_id,
            played_with_fish,
        )


async def user_show(self, ctx, tank_name, payload):
    """
    This command produces a gif of the specified tank.
    """

    # Typing Indicator
    async with ctx.typing():

        # variables
        fish_size_speed = {
            "Fish Bowl": 17,
            "Small Tank": 18,
            "Medium Tank": 25,
        }
        move_x = []
        im = []
        fishes = []
        fish_y_value = []
        files = []
        dead_alive = []
        fish_selections = []
        gif_name = random.randint(1, 1000)
        tank_slot = 0

        async with vbu.Database() as db:
            selected_fish = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""",
                ctx.author.id,
                tank_name,
            )
            tank_row = await db(
                """SELECT * FROM user_tank_inventory WHERE user_id =$1""",
                ctx.author.id,
            )

        # finds the tank slot
        for tank_slot_in in tank_row[0]["tank_name"]:
            if tank_slot_in == tank_name:
                break
            tank_slot += 1
        tank_info = tank_row[0]["tank_type"][tank_slot]

        # finds what type of fish it is, then adds the paths to a list, as well as finding the fish's random starting position
        for selected_fish_types in selected_fish:
            fishes.append(utils.Fish(name=selected_fish_types['fish_name'], level=selected_fish_types['fish_level'], current_xp=selected_fish_types['fish_xp'], max_xp=selected_fish_types['fish_xp_max'],
                                     alive=selected_fish_types['fish_alive'], species=utils.FishSpecies.get_fish(selected_fish_types['fish']), location_caught=selected_fish_types['fish_location'], skin=selected_fish_types['fish_skin']))

        # For each fish in the tank...
        for fish_object in fishes:

            move_x.append(
                random.randint(
                    min_max_x[tank_info][0],
                    min_max_x[tank_info][1],
                )
            )
            fish_y_value.append(
                random.randint(
                    min_max_y[tank_info][0],
                    min_max_y[tank_info][1],
                )
            )
            fish_selections.append(
                utils.get_normal_size_image(fish_object))

            dead_alive.append(fish_object.alive)

        # gif variables
        gif_filename = (
            f"{utils.file_prefix}/gifs/actual_gifs/user_tank{gif_name}.gif"
        )

        # Open our constant images
        tank_theme = tank_row[0]["tank_theme"][tank_slot]
        background = Image.open(
            f"{utils.file_prefix}/background/{tank_theme}_background_{utils.tank_types[tank_info]}.png"
        )
        midground = Image.open(
            f"{utils.file_prefix}/background/{tank_theme}_background_{utils.tank_types[tank_info]}_midground.png"
        )
        foreground = Image.open(
            f"{utils.file_prefix}/background/{utils.tank_types[tank_info]}.png"
        )
        for x in range(0, len(fish_selections)):
            im.append(Image.open(fish_selections[x]).convert("RGBA"))

        # For each frame of the gif...
        for _ in range(60):

            # Add a fish to the background image
            this_background = background.copy()

            # adds multiple fish and moves them if they are alive
            for x in range(0, len(im)):
                if dead_alive[x] is False:
                    this_background.paste(
                        im[x].rotate(180),
                        (move_x[x], fish_y_value[x]),
                        im[x].rotate(180),
                    )
                else:
                    this_background.paste(
                        im[x], (move_x[x], fish_y_value[x]), im[x]
                    )
                    move_x[x] += fish_size_speed[tank_info]
                    if move_x[x] > min_max_x[tank_info][1]:
                        move_x[x] = min_max_x[tank_info][0]

            # Pastes the backgrounds
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


async def user_entertain(self, ctx, tank_entertained, payload):
    async with vbu.Database() as db:
        tank_rows = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id = $1""",
            ctx.author.id,
        )
        upgrades = await db(
            """SELECT toys_upgrade, amazement_upgrade FROM user_upgrades WHERE user_id = $1""",
            ctx.author.id,
        )

    # Get the fish in the chosen tank
    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
            ctx.author.id,
            tank_entertained,
        )
        amount_of_crafted = await db(f"""SELECT fishing_boots FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)

    if not fish_rows:
        return await payload.response.send_message("No fish in that tank!")
    # Finds how much xp will be added, and if an extra level will be added
    total_xp_to_add = random.randint(
        utils.TOYS_UPGRADE[upgrades[0]["toys_upgrade"]][0],
        utils.TOYS_UPGRADE[upgrades[0]["toys_upgrade"]][1],
    )

    if amount_of_crafted:
        boot_multiplier = .3 * amount_of_crafted[0]['fishing_boots']
    else:
        boot_multiplier = 0
    total_xp_to_add * (1 + (boot_multiplier))
    extra_level = random.randint(
        1, utils.AMAZEMENT_UPGRADE[upgrades[0]["amazement_upgrade"]]
    )

    # set a new level check to true if theres an extra level
    if extra_level == 1:
        new_level = True
    else:
        new_level = False

    # Work out which slot the tank is in
    tank_slot = 0
    for tank_slots, tank_slot_in in enumerate(tank_rows[0]["tank_name"]):
        if tank_slot_in == tank_entertained:
            tank_slot = tank_slots
            break

    # See if they're able to entertain their tank due to the cooldown
    if tank_rows[0]["tank_entertain_time"][tank_slot]:
        if (
            tank_rows[0]["tank_entertain_time"][tank_slot]
            + timedelta(minutes=10)
            > dt.utcnow()
        ):
            time_left = timedelta(
                seconds=(
                    tank_rows[0]["tank_entertain_time"][tank_slot]
                    - dt.utcnow()
                    + timedelta(minutes=10)
                ).total_seconds()
            )
            relative_time = discord.utils.format_dt(
                dt.utcnow()
                + time_left
                - timedelta(hours=utils.DAYLIGHT_SAVINGS),
                style="R",
            )
            return await payload.response.send_message(
                f"This tank is entertained, please try again in {relative_time}.",
                ephemeral=True
            )

    # Typing Indicator
    async with ctx.typing():

        # For each fish add them to a list of fish names
        fish = []
        for single_fish in range(len(fish_rows)):
            fish.append(fish_rows[single_fish]["fish_name"])

        # Find the xp per fish and initiate the new data, and new line
        xp_per_fish = math.floor(total_xp_to_add / len(fish))
        new_fish_data = []
        n = "\n"

        # database...
        async with vbu.Database() as db:

            # Set the new time for when the tank was entertained
            await db(
                """UPDATE user_tank_inventory SET tank_entertain_time[$2] = $3 WHERE user_id = $1""",
                ctx.author.id,
                int(tank_slot + 1),
                dt.utcnow(),
            )

            # For each fish in the tank add their xp, gets the new fish's data
            for fish_name in fish:
                await utils.xp_finder_adder(
                    ctx.author.id, fish_name, xp_per_fish, new_level
                )
                new_fish_rows = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                    ctx.author.id,
                    fish_name,
                )
                new_fish_data.append(
                    [
                        new_fish_rows[0]["fish_name"],
                        new_fish_rows[0]["fish_level"],
                        new_fish_rows[0]["fish_xp"],
                        new_fish_rows[0]["fish_xp_max"],
                    ]
                )

            # Achievement added
            await db(
                """UPDATE user_achievements SET times_entertained = times_entertained + 1 WHERE user_id = $1""",
                ctx.author.id,
            )

    # The start of the display
    display_block = f"All fish have gained {xp_per_fish:,} XP{n}"

    # Add a string for each fish adding their new level and data
    for data in new_fish_data:
        display_block = (
            display_block
            + f"{data[0]} is now level {data[1]}, {data[2]}/{data[3]}{n}"
        )

    # Send the display string
    return await payload.response.send_message(display_block)


async def user_feed(self, ctx, tank_chosen):

    async with vbu.Database() as db:
        upgrades = await db(
            """SELECT feeding_upgrade, big_servings_upgrade FROM user_upgrades WHERE user_id = $1""",
            ctx.author.id,
        )
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""",
            ctx.author.id, tank_chosen
        )
        item_rows = await db(
            """SELECT * FROM user_item_inventory WHERE user_id = $1""",
            ctx.author.id,
        )

    # For each fish in the selected fish rows add them to a list
    if not fish_rows:
        return await ctx.send("No fish in that tank!")

    fish_in_tank = []
    for fish in fish_rows:
        feed_time = dt(year=2005, month=5, day=1)
        if fish["fish_feed_time"]:
            feed_time = fish["fish_feed_time"]
        if fish["fish_alive"] == True and not (fish_feed_timeout := feed_time + FISH_FEED_COOLDOWN) > dt.utcnow():
            fish_in_tank.append(fish["fish_name"])
    if len(fish_in_tank) != 0:
        if len(fish_in_tank) > 1:
            if item_rows[0]['super_food'] > 0:
                # Make the button check
                def yes_no_check(payload):
                    if payload.message.id != yes_no_message.id:
                        return False
                    self.bot.loop.create_task(payload.response.defer_update())
                    return payload.user.id == ctx.author.id

                components = discord.ui.MessageComponents(
                    discord.ui.ActionRow(
                        discord.ui.Button(
                            label="Yes", custom_id="yes"
                        ),
                        discord.ui.Button(
                            label="No", custom_id="no"
                        ),
                    ),
                )
                yes_no_message = await ctx.send(f"Would you like to use a Super Food to feed all fish in the tank? (You have {item_rows[0]['super_food']} and there are {len(fish_in_tank)} fish that need fed)", components=components)
                # Wait for them to click a button
                try:
                    chosen_button_payload = await self.bot.wait_for(
                        "component_interaction", timeout=60.0, check=yes_no_check
                    )
                    chosen_button = (
                        chosen_button_payload.component.custom_id.lower()
                    )
                except asyncio.TimeoutError:
                    await yes_no_message.edit(
                        components=components.disable_components()
                    )
                    chosen_button = "no"
                await yes_no_message.delete()
            else:
                chosen_button = "no"
            # Create a select menu of those fish
            if chosen_button == "yes":
                for fish_fed in fish_rows:
                    if fish_fed['fish_alive']:
                        # How many days and hours till the next feed based on upgrades
                        day, hour = utils.FEEDING_UPGRADES[upgrades[0]
                                                           ["feeding_upgrade"]]

                        # Set the time to be now + the new death date
                        death_date = fish_fed["death_time"] + timedelta(
                            days=day, hours=hour
                        )

                        # Update the fish's death date
                        async with vbu.Database() as db:
                            await db(
                                """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                                ctx.author.id,
                                fish_fed['fish_name'],
                                death_date,
                                dt.utcnow(),
                            )

                # Achievements
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_item_inventory SET super_food=super_food-1 WHERE user_id=$1""", ctx.author.id
                    )
                    await db(
                        """UPDATE user_achievements SET times_fed = times_fed + 1 WHERE user_id = $1""",
                        ctx.author.id,
                    )
                return await ctx.send(
                    f"All fish have been fed! <:AquaBonk:877722771935883265>"
                )
            fish_fed = await utils.create_select_menu(
                self.bot, ctx, fish_in_tank, "fish", "feed", True
            )
            if type(fish_fed) != str:
                return
        else:
            fish_fed = fish_in_tank[0]
        # Find the fish row of the selected fish
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
                ctx.author.id,
                fish_fed,
            )
        # See if the user has fish food for it
        if fish_row[0]["fish_level"] <= 20:
            type_of_food = "flakes"
        elif fish_row[0]["fish_level"] <= 50:
            type_of_food = "pellets"
        else:
            type_of_food = "wafers"
        # If they dont, tell them they have none
        if not item_rows[0][type_of_food] or item_rows[0][type_of_food] <= 0:
            return await ctx.send(f"You have no {type_of_food}!")
        # Make sure the fish is able to be fed
        if fish_row[0]["fish_feed_time"]:
            if (
                fish_feed_timeout := fish_row[0]["fish_feed_time"]
                + FISH_FEED_COOLDOWN
            ) > dt.utcnow():
                relative_time = discord.utils.format_dt(
                    fish_feed_timeout -
                    timedelta(hours=utils.DAYLIGHT_SAVINGS),
                    style="R",
                )
                return await ctx.send(
                    f"This fish is full, please try again {relative_time}."
                )
        # How many days and hours till the next feed based on upgrades
        day, hour = utils.FEEDING_UPGRADES[upgrades[0]
                                           ["feeding_upgrade"]]

        # Set the time to be now + the new death date
        death_date = fish_row[0]["death_time"] + timedelta(
            days=day, hours=hour
        )

        # Update the fish's death date
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET death_time = $3, fish_feed_time = $4 WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id,
                fish_fed,
                death_date,
                dt.utcnow(),
            )

            # If the fish is full it doesn't take up fish food (calculated with upgrades)
            extra = ""
            full = random.randint(
                1,
                utils.BIG_SERVINGS_UPGRADE[
                    upgrades[0]["big_servings_upgrade"]
                ],
            )
            if full != 1:
                await db(
                    """UPDATE user_item_inventory SET {0}={0}-1 WHERE user_id=$1""".format(
                        type_of_food
                    ),
                    ctx.author.id,
                )
            else:
                extra = "\nThat fish wasn't as hungry and didn't consume food!"

            # Achievements
            await db(
                """UPDATE user_achievements SET times_fed = times_fed + 1 WHERE user_id = $1""",
                ctx.author.id,
            )

        # And done
        return await ctx.send(
            f"**{fish_row[0]['fish_name']}** has been fed! <:AquaBonk:877722771935883265>{extra}"
        )
    else:
        return await ctx.send("No fish are hungry!")


async def user_clean(self, ctx, tank_cleaned, payload):
    # Get the fish, upgrades, and tank data from the database
    async with vbu.Database() as db:
        upgrades = await db(
            """SELECT bleach_upgrade, hygienic_upgrade, mutation_upgrade FROM user_upgrades WHERE user_id = $1""",
            ctx.author.id,
        )
        tank_rows = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id = $1""",
            ctx.author.id,
        )

    # Find the fish rows of all the fish in that tank
    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2 AND fish_alive = TRUE""",
            ctx.author.id,
            tank_cleaned,
        )

    if not fish_rows:
        return await payload.response.send_message("No fish in that tank!")
    # Work out which slot the tank is in
    tank_slot = 0
    for tank_slots, tank_slot_in in enumerate(tank_rows[0]["tank_name"]):
        if tank_slot_in == tank_cleaned:
            tank_slot = tank_slots
            break

    # Get the time before cleaning and the multiplier from upgrades
    multiplier, time = utils.HYGIENIC_UPGRADE[
        upgrades[0]["hygienic_upgrade"]
    ]

    # If its been enough time they can clean, else give an error
    if tank_rows[0]["tank_clean_time"][tank_slot]:
        if (
            tank_rows[0]["tank_clean_time"][tank_slot]
            + timedelta(minutes=time)
            > dt.utcnow()
        ):
            time_left = timedelta(
                seconds=(
                    tank_rows[0]["tank_clean_time"][tank_slot]
                    - dt.utcnow()
                    + timedelta(minutes=time)
                ).total_seconds()
            )
            relative_time = discord.utils.format_dt(
                dt.utcnow()
                + time_left
                - timedelta(hours=utils.DAYLIGHT_SAVINGS),
                style="R",
            )
            return await payload.response.send_message(
                f"This tank is clean, please try again {relative_time}.", ephemeral=True
            )

    # Initiate money gained, the rarity multiplier, and the size multiplier dictionaries
    money_gained = 0
    rarity_values = {
        "common": 1.0,
        "uncommon": 1.2,
        "rare": 1.4,
        "epic": 1.6,
        "legendary": 1.8,
        "mythic": 2.0,
    }
    size_values = {"small": 0, "medium": 2, "large": 14}

    # Randomly pick the effort extra
    effort_extra = random.choices([0, 5, 15], [0.6, 0.3, 0.1])

    # Initiate the size, extra, and rarity variables
    size_multiplier = 1
    extra = ""
    rarity_multiplier = 0

    # For each fish in the tank...
    for fish in fish_rows:

        # See if they mutate with the mutate upgrade
        mutate = random.randint(
            1, utils.MUTATION_UPGRADE[upgrades[0]["mutation_upgrade"]]
        )

        if mutate == 1:
            async with vbu.Database() as db:
                await db(
                    """UPDATE user_fish_inventory SET fish_skin = $1 where user_id = $2 AND fish = $3""",
                    "inverted",
                    ctx.author.id,
                    fish["fish"],
                )
                nl = "\n"
                extra += f"{nl}{fish['fish']} looks kind of strange now..."

        fish_species = utils.FishSpecies.get_fish(fish['fish'])
        size_multiplier = size_values[fish_species.size]
        rarity_multiplier = rarity_values[fish_species.rarity]

        # The money added for each fish is the level * the rarity * the size
        money_gained += (
            fish["fish_level"] * (rarity_multiplier + size_multiplier)
        )

    # See if they voted, and if so add a .5 to the multipliers
    vote_multiplier = 0
    if await utils.get_user_voted(self.bot, ctx.author.id) == True:
        vote_multiplier = .5
        await ctx.send(
            "You voted at <https://top.gg/bot/840956686743109652/vote> for a **1.5x** bonus to money earned"
        )

    # After all the fish the new money is the total * upgrade multipliers + the effort rounded down
    money_gained = math.floor(money_gained * (utils.BLEACH_UPGRADE[upgrades[0]["bleach_upgrade"]] + (
        multiplier - 1) + vote_multiplier) + effort_extra[0])

    # Add the money gained to the database, and add the achievements
    async with vbu.Database() as db:
        await db(
            """UPDATE user_tank_inventory SET tank_clean_time[$2] = $3 WHERE user_id = $1""",
            ctx.author.id,
            int(tank_slot + 1),
            dt.utcnow(),
        )
        await db(
            """UPDATE user_balance SET balance = balance + $2 WHERE user_id = $1""",
            ctx.author.id,
            int(money_gained),
        )
        # Achievements
        await db(
            """UPDATE user_achievements SET times_cleaned = times_cleaned + 1 WHERE user_id = $1""",
            ctx.author.id,
        )
        await db(
            """UPDATE user_achievements SET money_gained = money_gained + $2 WHERE user_id = $1""",
            ctx.author.id,
            int(money_gained),
        )

    # And were done, send it worked
    await payload.response.send_message(
        f"You earned **{money_gained}** <:sand_dollar:877646167494762586> for cleaning that tank! <:AquaSmile:877939115994255383>{extra}"
    )
    return True


async def user_revive(self, ctx, tank):
    # Get database vars

    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_alive = FALSE AND tank_fish = $2""",
            ctx.author.id, tank
        )
        revival_count = await db(
            """SELECT revival FROM user_item_inventory WHERE user_id = $1""",
            ctx.author.id,
        )

    # Make a list of all their fish
    fish_in_tank = []
    for fish in fish_rows:
        fish_in_tank.append(fish["fish_name"])

    # Create a select menu with their fish being choices
    fish = await utils.create_select_menu(
        self.bot, ctx, fish_in_tank, "dead fish", "revive", True
    )

    if revival_count[0]['revival'] <= 0:
        return await ctx.send("You have no revivals!")

    # If the fish isn't in a tank, it has no death timer, but if it is it's set to three days
    death_timer = dt.utcnow() + timedelta(days=3)
    message = f"{fish} is now alive, and will die {discord.utils.format_dt(death_timer, style='R')}!"

    # Set the database values
    async with vbu.Database() as db:
        await db(
            """UPDATE user_fish_inventory SET fish_alive = True, death_time = $3 WHERE user_id = $1 AND fish_name = $2""",
            ctx.author.id,
            fish,
            death_timer,
        )
        await db(
            """UPDATE user_item_inventory SET revival = revival - 1 WHERE user_id = $1""",
            ctx.author.id,
        )

    # Send message
    await ctx.send(
        message, allowed_mentions=discord.AllowedMentions.none()
    )


async def user_remove(self, ctx, tank_name):
    # variables for size value and the slot the tank is in
    size_values = {"small": 1, "medium": 5, "large": 25}
    tank_slot = 0

    async with vbu.Database() as db:
        fish_rows = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""",
            ctx.author.id,
            tank_name,
        )

    # Make a list of all their fish
    if not fish_rows:
        return await ctx.send("No fish in that tank!")
    fish_in_tank = []
    for fish in fish_rows:
        fish_in_tank.append(fish["fish_name"])

    # Create a select menu with their fish being choices
    fish_removed = await utils.create_select_menu(
        self.bot, ctx, fish_in_tank, "fish", "remove", True
    )
    if not fish_removed:
        return

    async with vbu.Database() as db:
        tank_row = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id =$1""",
            ctx.author.id,
        )
        fish_row = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2 AND tank_fish != ''""",
            ctx.author.id,
            fish_removed,
        )
        item_rows = await db(
            """SELECT * FROM user_item_inventory WHERE user_id = $1""",
            ctx.author.id,
        )

    # See if the user has fish food for it
    if fish_row[0]["fish_level"] <= 20:
        type_of_food = "flakes"
    elif fish_row[0]["fish_level"] <= 50:
        type_of_food = "pellets"
    else:
        type_of_food = "wafers"

    # If they dont, tell them they have none
    if fish_row[0]["fish_alive"] == True:
        if not item_rows[0][type_of_food]:
            return await ctx.send(f"You must have a piece of {type_of_food} before you can remove this fish so it doesn't go hungry! (after getting food run this command again)")

    # finds the tank slot the tank in question is at
    tank_name = fish_row[0]['tank_fish']
    for tank_slot_in in tank_row[0]["tank_name"]:
        if tank_slot_in == tank_name:
            break
        tank_slot += 1

    # Change between sql arrays and python arrays
    tank_slot += 1

    # Update the fish being removed and the tank's room
    async with vbu.Database() as db:
        if fish_row[0]["fish_alive"] == True:
            await db(
                """UPDATE user_item_inventory SET {0}={0}-1 WHERE user_id=$1""".format(
                    type_of_food
                ),
                ctx.author.id,
            )
        await db(
            """UPDATE user_fish_inventory SET tank_fish = '', death_time = NULL, fish_remove_time = $3 WHERE user_id = $1 AND fish_name = $2""",
            ctx.author.id,
            fish_removed,
            (dt.utcnow() + timedelta(days=5)),
        )
        await db(
            """UPDATE user_tank_inventory SET fish_room[$3] = fish_room[$3] + $2 WHERE user_id = $1""",
            ctx.author.id,
            int(size_values[fish_row[0]["fish_size"]]),
            tank_slot,
        )

    # Confirmation message
    return await ctx.send(
        f"**{fish_removed}** removed from **{tank_name}**!",
        allowed_mentions=discord.AllowedMentions.none(),
    )


async def user_deposit(self, ctx, tank_name, chosen_button_payload):
    # variables for size value and the slot the tank is in
    size_values = {"small": 1, "medium": 5, "large": 25}

    try:
        fish_deposited, interaction = await utils.create_modal(self.bot, chosen_button_payload, "Fish Deposited", "Enter Your Fish's Name")
    except TypeError:
        return await ctx.send("Modal timed out.")

    async with vbu.Database() as db:
        fish_row = await db(
            """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
            ctx.author.id,
            fish_deposited,
        )
        tank_row = await db(
            """SELECT * FROM user_tank_inventory WHERE user_id =$1""",
            ctx.author.id,
        )

    # all the checks for various reasons the command shouldn't be able to work
    if not fish_row:
        if interaction:
            interaction.response.defer_update()
        return await ctx.send(
            f"You have no fish named **{fish_deposited}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )
    if fish_row[0]["tank_fish"]:
        return await interaction.response.send_message("This fish is already in a tank!")
    if fish_row[0]["fish_alive"] is False:
        return await interaction.response.send_message("That fish is dead!")

    # finds the tank slot the tank in question is at
    for tank_slot, tank_slot_in in enumerate(tank_row[0]["tank_name"]):
        if tank_slot_in == tank_name:
            break

    # another check
    if (
        tank_row[0]["fish_room"][tank_slot]
        < size_values[fish_row[0]["fish_size"]]
    ):
        n = "\n"
        return await interaction.response.send_message(
            f"{fish_row[0]['fish_name']} is {fish_row[0]['fish_size']} and takes up {size_values[fish_row[0]['fish_size']]} Size Points.{n}That tank only has {tank_row[0]['fish_room'][tank_slot]} Size Points left"
        )

    # tank slot has one added as python indexes start at 0 but database start at 1
    tank_slot += 1

    # add the fish to the tank in the database
    async with vbu.Database() as db:
        await db(
            """UPDATE user_tank_inventory SET fish_room[$2] = fish_room[$2] - $3 WHERE user_id=$1""",
            ctx.author.id,
            tank_slot,
            size_values[fish_row[0]["fish_size"]],
        )
        await db(
            """UPDATE user_fish_inventory SET tank_fish = $3, death_time = $4 WHERE fish_name=$1 AND user_id=$2""",
            fish_deposited,
            ctx.author.id,
            tank_name,
            (dt.utcnow() + timedelta(days=3)),
        )

    # find the timestamp in relative time of when the fish will die
    relative_time = discord.utils.format_dt(
        dt.utcnow()
        + timedelta(days=3)
        - timedelta(hours=utils.DAYLIGHT_SAVINGS),
        style="R",
    )

    # Confirmation message
    return await ctx.send(
        f"Fish has been deposited and will die {relative_time}!"
    )


async def user_info(self, ctx, tank_info, fishes):
    tank_types = {"Fish Bowl": 1, "Small Tank": 5, "Medium Tank": 25}
    info_title = f"Tank Name: {tank_info[5]}"
    info_field = f"{utils.EMOJIS['bar_empty']}Tank Type: {tank_info[0]}\n{utils.EMOJIS['bar_empty']}Tank Room: {tank_info[2]}/{tank_types[tank_info[0]]}"
    for fish in fishes:
        info_field += f"\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}Fish Name: {fish.name}\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}Type: {fish.species.name.replace('_', ' ').title()}\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}Level: {fish.level}"
        if fish.skin != "":
            info_field += f"\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}Skin: {fish.skin}"
    fixed_fields = utils.get_fixed_field((info_title, info_field))
    await utils.paginate(ctx, fixed_fields, ctx.author,
                         f"{ctx.author.display_name}'s Tank")
