import random
import asyncio
from datetime import datetime as dt, timedelta
import io

from PIL import Image
import imageio
import discord
from discord.ext import commands, vbu

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS, Fish, FishSpecies


class Aquarium(vbu.Cog):
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def firsttank(self, ctx: commands.Context):
        """
        This command gives the user their first tank.
        """

        # See if they already have a tank
        async with vbu.Database() as db:
            fetched = await db(
                """SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""",
                ctx.author.id,
            )
        if fetched:
            return await ctx.send("You have your first tank already!")

        # Add a tank to the user
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES ($1);""",
                ctx.author.id,
            )
            await db(
                """UPDATE user_tank_inventory SET tank[1]=TRUE, tank_type[1]='Fish Bowl',
                fish_room[1] = 1, tank_theme[1] = 'Aqua' WHERE user_id=$1""",
                ctx.author.id,
            )

        def button_check(payload):
            if payload.message.id != message.id:
                return False
            return payload.user.id == ctx.author.id

        # Add the buttons to the message
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(emoji=utils.EMOJIS["aqua_smile"]),
            ),
        )
        # Asks what to name the new tank and makes sure it matches the check
        message = await ctx.send(
            "What would you like to name this tank? "
            "(must be a different name from your other tanks, "
            'less than 32 characters, and cannot be "none")',
            components=components
        )

        # Wait for them to click a button
        try:
            chosen_button_payload = await self.bot.wait_for(
                "component_interaction", timeout=60.0, check=button_check
            )
        except asyncio.TimeoutError:
            name = "Starter Tank"
            await ctx.send(
                f"Did you forget about me {ctx.author.mention}? I've been waiting for a while "
                f"now! I'll name the tank for you. Let's call it **{name}**."
            )

        try:
            name, interaction2 = await utils.create_modal(self.bot, chosen_button_payload, "Tank Name", "Enter your new tank's name")
            if interaction2:
                await interaction2.response.defer()
        except TypeError:
            name = None

        if not name:
            name = "Starter Tank"
            await ctx.send(
                f"Did you forget about me {ctx.author.mention}? I've been waiting for a while "
                f"now! I'll name the tank for you. Let's call it **{name}**."
            )

        await ctx.send(
            f"You have your new tank, **{name}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

        # Save their tank name
        async with vbu.Database() as db:
            await db(
                """UPDATE user_tank_inventory SET tank_name[1]=$1 WHERE user_id=$2;""",
                name,
                ctx.author.id,
            )

    @commands.command(enabled=False)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def preview(self, ctx: commands.Context, theme: str):
        """
        Previews a tank theme
        """

        # Makes sure what they enter is in titlecase
        theme = theme.title()

        # Check if that tank theme exists
        if theme not in utils.TANK_THEMES:
            return await ctx.send("That is not a valid tank theme!")

        # Find which tank theme they want
        tank_themes = [(utils.PLANT_LIFE_NAMES, "Plant_Life")]
        for themes in tank_themes:
            if theme in themes[0]:
                theme_chosen = themes[1]

        # Dict of all the tank types
        tank_types = {
            "Fish Bowl": "fishbowl",
            "Small Tank": "Small_Tank_2D",
            "Medium Tank": "Medium_Tank_2D",
        }

        # Create a select meny for the tank types
        tank_type = await utils.create_select_menu(
            self.bot, ctx, tank_types.keys(), "tank type", "choose"
        )

        # Set up the image
        file_prefix = "C:/Users/JT/Pictures/Aqua/assets/images"
        image = f"{file_prefix}/background/tank_theme_previews/{theme_chosen}_{tank_types[tank_type]}_preview.png"

        # Display the chosen theme on the chosen tank type
        await ctx.send(file=discord.File(image))


def setup(bot):
    bot.add_cog(Aquarium(bot))
