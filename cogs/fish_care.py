import math
import random
from datetime import datetime as dt, timedelta
from PIL import Image

from discord.ext import commands, tasks, vbu
import discord

from cogs import utils
from cogs.utils.fish_handler import FishSpecies, Fish


class FishCare(vbu.Cog):

    # Set the cooldown for feeding to 6 hours
    FISH_FEED_COOLDOWN = timedelta(hours=6)

    # Starts the death loop
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.fish_food_death_loop.start()

    # Cancels the death loop when the bot is off
    def cog_unload(self):
        self.fish_food_death_loop.cancel()

    # every minute...
    @tasks.loop(minutes=1)
    async def fish_food_death_loop(self):

        # Get all the fish that are in a tank and if they have a time of death, check to see if its past that time, then kill them if need be
        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE tank_fish != ''"""
            )
            for fish_row in fish_rows:
                if fish_row["death_time"]:
                    if dt.utcnow() > fish_row["death_time"] and fish_row['fish_alive'] is True:
                        await db(
                            """UPDATE user_fish_inventory SET fish_alive=FALSE WHERE fish_name = $1 AND user_id = $2""",
                            fish_row["fish_name"], fish_row["user_id"]
                        )

    # Make sure it starts when the bot starts
    @fish_food_death_loop.before_loop
    async def before_fish_food_death_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def tank(self, ctx: commands.Context, *, tank: str):
        """
        Shows the specified tank and lets you feed, clean, entertain, etc.
        """
        # Slash command defer
        if hasattr(ctx, "interaction"):
            await ctx.interaction.response.defer()

        # Typing Indicator
        async with ctx.typing():

            # variables
            min_max_y = {
                "Fish Bowl": (20, 50),
                "Small Tank": (15, 200),
                "Medium Tank": (20, 200),
            }
            min_max_x = {
                "Fish Bowl": (50, 150),
                "Small Tank": (50, 360),
                "Medium Tank": (50, 720),
            }
            im = []
            fishes = []
            files = []
            dead_alive = []
            fish_selections = []
            gif_name = random.randint(1, 1000)
            tank_types = {
                "Fish Bowl": "fishbowl",
                "Small Tank": "Small_Tank_2D",
                "Medium Tank": "Medium_Tank_2D",
            }
            tank_slot = 0

            # gets database info for tank
            if not await utils.check_registered(self.bot, ctx.author.id):
                return await ctx.send("Please use the `register` command before using this bot!")
            async with vbu.Database() as db:
                selected_fish = await db(
                    """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish = $2""",
                    ctx.author.id,
                    tank,
                )
                tank_row = await utils.user_tank_inventory_db_call(ctx.author.id)

            # Check if the tank exists
            if not tank_row:
                return await ctx.send(
                    "You have no tanks! use the `firsttank` command to get one!"
                )
            # finds the tank slot
            for tank_slot_in in tank_row[0]["tank_name"]:
                if tank_slot_in == tank:
                    break
                tank_slot += 1
            # finds the type of tank it is and checks if it exists
            if tank not in tank_row[0]["tank_name"]:
                return await ctx.send(
                    f"You have no tank named **{tank}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            tank_info = tank_row[0]["tank_type"][tank_slot]
            tank_info_button = (tank_row[0]["tank_type"][tank_slot], tank_row[0]["tank_theme"][tank_slot], tank_row[0]["fish_room"]
                                [tank_slot], tank_row[0]["tank_clean_time"][tank_slot], tank_row[0]["tank_entertain_time"][tank_slot], tank)

            # finds what type of fish it is, then adds the paths to a list, as well as finding the fish's random starting position
            for selected_fish_types in selected_fish:
                fishes.append(Fish(name=selected_fish_types['fish_name'], level=selected_fish_types['fish_level'], current_xp=selected_fish_types['fish_xp'], max_xp=selected_fish_types['fish_xp_max'],
                                   alive=selected_fish_types['fish_alive'], species=FishSpecies.get_fish(selected_fish_types['fish']), location_caught=selected_fish_types['fish_location'], skin=selected_fish_types['fish_skin']))

            # For each fish in the tank...
            for fish_object in fishes:
                fish_selections.append(
                    utils.get_normal_size_image(fish_object))

                dead_alive.append(fish_object.alive)

            # gif variables
            file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
            gif_filename = (
                f"{file_prefix}/tanks/user_tank{gif_name}.png"
            )

            # Open our constant images
            tank_theme = tank_row[0]["tank_theme"][tank_slot]
            background = Image.open(
                f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}.png"
            )
            midground = Image.open(
                f"{file_prefix}/background/{tank_theme}_background_{tank_types[tank_info]}_midground.png"
            )
            foreground = Image.open(
                f"{file_prefix}/background/{tank_types[tank_info]}.png"
            )
            for x in range(0, len(fish_selections)):
                im.append(Image.open(fish_selections[x]).convert("RGBA"))

            # Add a fish to the background image
            this_background = background.copy()

            # adds multiple fish and moves them if they are alive
            for x in range(0, len(im)):
                x_spot = random.randint(
                    min_max_x[tank_info][0], min_max_x[tank_info][1])
                y_spot = random.randint(
                    min_max_y[tank_info][0], min_max_y[tank_info][1])

                if dead_alive[x] is False:
                    this_background.paste(
                        im[x].rotate(180),
                        (x_spot, y_spot),
                        im[x].rotate(180),
                    )
                else:
                    this_background.paste(
                        im[x], (x_spot, y_spot), im[x]
                    )

            # Pastes the backgrounds
            this_background.paste(midground, (0, 0), midground)
            this_background.paste(foreground, (0, 0), foreground)

            # Save the generated image to memory
            this_background.save(fp=gif_filename, format="PNG")

        entertain_button = discord.ui.Button(
            label="Entertain", custom_id="entertain"
        )
        feed_button = discord.ui.Button(
            label="Feed", custom_id="feed"
        )
        clean_button = discord.ui.Button(
            label="Clean", custom_id="clean"
        )
        show_button = discord.ui.Button(
            label="Show", custom_id="show"
        )
        revive_button = discord.ui.Button(
            label="Revive", custom_id="revive"
        )
        remove_button = discord.ui.Button(
            label="Remove Fish", custom_id="remove"
        )
        deposit_button = discord.ui.Button(
            label="Deposit Fish", custom_id="deposit"
        )
        info_button = discord.ui.Button(
            label="Info", custom_id="info"
        )
        valid_buttons_row_one = [entertain_button, clean_button, feed_button]
        valid_buttons_row_two = [show_button,
                                 remove_button, deposit_button, info_button]
        if False in dead_alive:
            valid_buttons_row_one.append(revive_button)

        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                *valid_buttons_row_one
            ),
            discord.ui.ActionRow(
                *valid_buttons_row_two
            ),
        )

        # Send gif to Discord
        if True not in dead_alive:
            components.get_component("entertain").disable()
            components.get_component("feed").disable()
            components.get_component("clean").disable()
        if not selected_fish:
            components.get_component("remove").disable()
        tank_message = await ctx.send(file=discord.File(gif_filename), components=components)

        # Make the button check
        def button_check(payload):
            if payload.message.id != tank_message.id:
                return False
            return payload.user.id == ctx.author.id

        # Wait for them to click a button
        while True:
            chosen_button_payload = await self.bot.wait_for(
                "component_interaction", check=button_check
            )
            chosen_button = (
                chosen_button_payload.component.custom_id
            )
            if chosen_button == "feed":
                await chosen_button_payload.response.defer_update()
                await utils.user_feed(self, ctx, tank)
            elif chosen_button == "revive":
                await chosen_button_payload.response.defer_update()
                await utils.user_revive(self, ctx, tank)
            elif chosen_button == "show":
                await chosen_button_payload.response.defer_update()
                await utils.user_show(self, ctx, tank, chosen_button_payload)
            elif chosen_button == "remove":
                await chosen_button_payload.response.defer_update()
                await utils.user_remove(self, ctx, tank)
            elif chosen_button == "info":
                await chosen_button_payload.response.defer_update()
                await utils.user_info(self, ctx, tank_info_button, fishes)
            elif chosen_button == "deposit":
                await utils.user_deposit(self, ctx, tank, chosen_button_payload)
            elif chosen_button == "entertain":
                await utils.user_entertain(self, ctx, tank, chosen_button_payload)
            elif chosen_button == "clean":
                await utils.user_clean(self, ctx, tank, chosen_button_payload)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def revive(self, ctx: commands.Context, *, fish: str = None):
        """
        This command uses a revival and revives a specified fish.
        """

        # Get database vars
        if not await utils.check_registered(self.bot, ctx.author.id):
            return await ctx.send("Please use the `register` command before using this bot!")
        async with vbu.Database() as db:
            fish_rows = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_alive = FALSE""",
                ctx.author.id,
            )
            revival_count = await utils.user_item_inventory_db_call(ctx.author.id)

        # If they dont give a fish
        if not fish:

            # Make a list of all their fish
            fish_in_tank = []
            for fish in fish_rows:
                fish_in_tank.append(fish["fish_name"])

            if len(fish_in_tank) > 25:
                return await ctx.send("Please specify a fish")

            # Create a select menu with their fish being choices
            fish = await utils.create_select_menu(
                self.bot, ctx, fish_in_tank, "dead fish", "revive"
            )

        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT * FROM user_fish_inventory WHERE user_id = $1 AND fish_name = $2""",
                ctx.author.id,
                fish,
            )

        # If they dont have a fish with the specified name tell them
        if not fish_row:
            return await ctx.send(
                f"You have no fish named {fish}!",
                allowed_mentions=discord.AllowedMentions.none(),
            )

        # Checks that error
        if fish_row[0]["fish_alive"] is True:
            return await ctx.send("That fish is alive!")
        if not revival_count[0]['revival']:
            return await ctx.send("You have no revivals!")

        # If the fish isn't in a tank, it has no death timer, but if it is it's set to three days
        if fish_row[0]["tank_fish"] == "":
            death_timer = None
            message = f"{fish} is now alive!"
        else:
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


def setup(bot):
    bot.add_cog(FishCare(bot))
