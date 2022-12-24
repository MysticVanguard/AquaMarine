import random
import asyncio
import discord
from datetime import datetime as dt, timedelta
from discord.ext import commands, tasks, vbu
import math

from cogs import utils
from cogs.utils import EMOJIS
from cogs.utils.fish_handler import FishSpecies


class Fishing(vbu.Cog):
    cast_time = dt.utcnow()

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.user_cast_loop.start()

    def cog_unload(self):
        self.user_cast_loop.cancel()

    # Every hour, everyone gets a cast as long as they have less than 50
    @tasks.loop(minutes=45)
    async def user_cast_loop(self):
        self.cast_time = dt.utcnow()
        async with vbu.Database() as db:
            casts = await db("""SELECT * FROM user_balance""")
            for x in casts:
                if x["casts"] >= 64:
                    continue
                amount_of_crafted = await utils.user_item_inventory_db_call(
                    x["user_id"])
                if amount_of_crafted:
                    if amount_of_crafted[0]['fishing_boots'] <= 5:
                        boot_multiplier = amount_of_crafted[0]['fishing_boots']
                    else:
                        boot_multiplier = 5
                else:
                    boot_multiplier = 0
                amount = random.choices(
                    [1, 2], [(1 - (.03 * boot_multiplier)), (.03 * boot_multiplier)])[0]
                await db(
                    """UPDATE user_balance SET casts=casts+$2 WHERE user_id = $1""",
                    x["user_id"], amount
                )
            fish_in_tanks = await db("""SELECT * FROM user_fish_inventory WHERE tank_fish != '' AND fish_alive = TRUE""")
            for y in fish_in_tanks:
                amount_of_trash_toys = await utils.user_item_inventory_db_call(
                    y["user_id"])
                amount_of_xp = await utils.user_upgrades_db_call(y['user_id'])
                total_xp = math.ceil((utils.TOYS_UPGRADE[amount_of_xp[0]['toys_upgrade']]
                                      [0] * .25) * (.25 * amount_of_trash_toys[0]['trash_toys']))
                await utils.xp_finder_adder(y['user_id'], y['fish_name'], total_xp, False)

    @user_cast_loop.before_loop
    async def before_user_cast_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta()
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        This command catches a fish.
        """

        await utils.check_registered(self.bot, ctx, ctx.author.id)
        # await ctx.interaction.response.defer()

        # Fetch all of their data
        async with vbu.Database() as db:
            upgrades = await utils.user_upgrades_db_call(ctx.author.id)
            casts = await utils.user_balance_db_call(ctx.author.id)
            user_locations_info = await utils.user_location_info_db_call(
                ctx.author.id)
            user_inventory = await utils.user_fish_inventory_db_call(ctx.author.id)
            user_item_inventory = await utils.user_item_inventory_db_call(ctx.author.id)
            location_pools_info = await utils.fish_pool_location_db_call()

            if not user_locations_info:
                user_locations_info = await db(
                    """INSERT INTO user_location_info (user_id, current_location) VALUES ($1, 'pond') RETURNING *""",
                    ctx.author.id
                )

        # Send fish menu
        embed = discord.Embed(
            title=f"__{ctx.author.display_name}'s Fish Menu!__\n*Current Location: {user_locations_info[0]['current_location'].replace('_', ' ').title()}*")
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/952006920858923060/1035613173274918912/fishing_idle.gif")
        for rarity, fish in FishSpecies.all_species_by_location_rarity[user_locations_info[0]['current_location']].items():
            rarity = rarity.upper()
            fish_in_rarity = []
            for single_fish in fish:
                if user_locations_info[0][f"{single_fish.name}_caught"] > 0:
                    fish_in_rarity.append(
                        f"{single_fish.name.replace('_', ' ').title()} ({location_pools_info[0][f'{single_fish.name}_count']} Left)")
                else:
                    fish_in_rarity.append(
                        f"??? ({location_pools_info[0][f'{single_fish.name}_count']} Left)\t")
            embed.add_field(name=rarity, value='\n'.join(
                [f"{fish}" for fish in fish_in_rarity]), inline=True)
        effect_string = "** **"
        for effect in ["recycled_fishing_rod", "recycled_bait", "recycled_fish_hook", "recycled_fish_finder"]:
            amount = user_item_inventory[0][effect]
            formatted_effect = effect.replace("_", " ").title()
            if amount > 0:
                effect_string += f"{formatted_effect}: {amount} casts left to apply to\n"
        embed.add_field(name="Effects", value=effect_string)

        # Create fish menu options and send everything
        components = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(label="Fish", custom_id="fish"),
                discord.ui.Button(label="Change Location",
                                  custom_id="change_location"),
                discord.ui.Button(label="Unlock Location", custom_id="unlock"),
                discord.ui.Button(label="Close Menu", custom_id="close_menu")
            ),
        )
        if user_item_inventory[0]['new_location_unlock'] < 1:
            components.get_component('unlock').disable()
        fish_menu_message = await ctx.send(embed=embed, components=components)
        unlockable_locations = ["coral_reef",
                                "ocean", "deep_sea", "river", "lake"]

        # Wait for them to click a button
        menu_open = True
        while menu_open:
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=120, check=lambda p: p.user.id == ctx.author.id and p.message.id == fish_menu_message.id
                )
                fish_chosen_button_payload = chosen_button_payload
                chosen_button = (
                    chosen_button_payload.component.custom_id
                )
            except asyncio.TimeoutError:
                await fish_menu_message.edit(components=components.disable_components())
                chosen_button = ""
                menu_open = False

            # If they choose to fish:
            if chosen_button == "fish":
                await chosen_button_payload.response.defer_update()
                keep_fishing = True
                while keep_fishing:
                    async with vbu.Database() as db:
                        casts = await utils.user_balance_db_call(ctx.author.id)
                        user_inventory = await utils.user_fish_inventory_db_call(ctx.author.id)

                    # If they have no casts tell them they can't fish
                    if casts[0]["casts"] <= 0:
                        relative_time = discord.utils.format_dt(
                            self.cast_time + timedelta(minutes=45) -
                            timedelta(hours=(utils.DAYLIGHT_SAVINGS - 2)),
                            style="R",
                        )
                        return await ctx.send(f"You have no casts, You will get another {relative_time}.")

                    returned_message, post_components = await utils.user_fish(self, ctx, casts, upgrades,
                                                                              user_locations_info, user_inventory, location_pools_info)

                    if not returned_message:
                        return
                    refish_message = await ctx.send(returned_message, components=post_components)

                    # Wait for them to click a button
                    try:
                        fish_chosen_button_payload = await self.bot.wait_for(
                            "component_interaction", timeout=60.0, check=lambda p: p.user.id == ctx.author.id)
                        chosen_button = fish_chosen_button_payload.component.custom_id.lower()
                    except asyncio.TimeoutError:
                        keep_fishing = False
                    if chosen_button == "stop":
                        keep_fishing = False
                        await fish_chosen_button_payload.response.defer_update()
                    await refish_message.delete()

                # Find if they catch a crate with the crate_chance_upgrade
                crate_catch = random.randint(
                    1, utils.CRATE_CHANCE_UPGRADE[upgrades[0]
                                                  ["crate_chance_upgrade"]]
                )

                # If they caught it...
                if crate_catch == 1:
                    crate_loot = []

                    # Choose a random crate tier based on their crate_tier_upgrade and add the loot for that tier
                    crate = random.choices(("Wooden", "Bronze", "Steel", "Golden", "Diamond",
                                           "Enchanted",), utils.CRATE_TIER_UPGRADE[upgrades[0]["crate_tier_upgrade"]])
                    crate_loot.append(("balance", random.randint(
                        0, utils.CRATE_TIERS[crate[0]][0]), "user_balance"))
                    crate_loot.append(("casts", random.randint(
                        0, utils.CRATE_TIERS[crate[0]][1]), "user_balance"))
                    crate_loot.append((random.choices(("none", "cfb", "ufb", "rfb", "ifb", "hlfb"), utils.CRATE_TIERS[crate[0]][2])[
                                      0], random.randint(0, utils.CRATE_TIERS[crate[0]][3]), "user_inventory"))
                    crate_loot.append((random.choices(("none", "flakes", "pellets", "wafers"), utils.CRATE_TIERS[crate[0]][4])[
                                      0], random.randint(0, utils.CRATE_TIERS[crate[0]][5]), "user_inventory"))
                    crate_loot.append((random.choices(("none", "fullness", "experience", "mutation"), utils.CRATE_TIERS[crate[0]][6])[
                                      0], random.randint(0, utils.CRATE_TIERS[crate[0]][7]), "user_inventory"))

                    # Initialize variables and display variable for every item
                    crate_message = ""
                    nl = "\n"
                    display = {"balance": "Sand Dollars", "casts": "Casts",
                               "cfb": "Common Fish Bags", "ufb": "Uncommon Fish Bags",
                               "rfb": "Rare Fish Bags", "ifb": "Inverted Fish Bags",
                               "hlfb": "High Level Fish Bags", "flakes": "Fish Flakes",
                               "pellets": "Fish Pellets", "wafers": "Fish Wafers",
                               "experience": "Experience Potions", "mutation": "Mutation Potions",
                               "fullness": "Fullness Potions",
                               }

                    async with vbu.Database() as db:
                        # For each piece of loot in the crate
                        for data in crate_loot:

                            # Unpack the data
                            type_of_loot, amount_of_loot, table_of_loot = data
                            # If the type isn't "none" and there is an amount insert the loot into their database
                            if type_of_loot != "none" and amount_of_loot != 0:
                                await db(
                                    """UPDATE {0} SET {1} = {1} + $2 WHERE user_id = $1""".format(
                                        table_of_loot, type_of_loot
                                    ),
                                    ctx.author.id,
                                    amount_of_loot,
                                )
                                # Add a message to the end of the string to be sent
                                crate_message += f"{nl}{amount_of_loot}x {display[type_of_loot]} recieved!"

                        # Send the message telling them they caught a crate and what was in it
                        await ctx.channel.send(
                            f"{ctx.author.display_name} caught a {crate[0]} crate containing: {crate_message}"
                        )
            elif chosen_button == "change_location":

                # Give a dropdown with their locations that are unlocked
                await chosen_button_payload.response.defer_update()
                locations = ["pond", "creek", "estuary"]
                specific_locations = []
                for location in locations:
                    if location == user_locations_info[0]['current_location']:
                        continue
                    specific_locations.append(
                        location.replace('_', ' ').title())
                for location in unlockable_locations:
                    if (user_locations_info[0][f'{location}_unlocked'] or user_item_inventory[0]["recycled_waders"] > 0) and not location == user_locations_info[0]['current_location']:
                        specific_locations.append(
                            location.replace('_', ' ').title())

                # Send select menu, update their location and say they traveled
                location_choice = await utils.create_select_menu(
                    self.bot, ctx, specific_locations, "location", "choose", True
                )
                if type(location_choice) == str:
                    location = location_choice.replace(' ', '_').lower()
                    async with vbu.Database() as db:
                        await db("""UPDATE user_location_info SET current_location = $2 WHERE user_id = $1""", ctx.author.id, location)
                        if user_item_inventory[0]["recycled_waders"] > 0:
                            await db("""UPDATE user_item_inventory SET recycled_waders = recycled_waders - 1 WHERE user_id = $1""",
                                     ctx.author.id)
                    await ctx.send(
                        f"Traveled to {location_choice}")
            elif chosen_button == 'unlock':

                # Send a drop down with the locations able to be unlocked
                await chosen_button_payload.response.defer_update()
                specific_unlockable_locations = []
                for location in unlockable_locations:
                    if not user_locations_info[0][f'{location}_unlocked']:
                        specific_unlockable_locations.append(
                            location.replace('_', ' ').title())
                if len(specific_unlockable_locations) == 0:
                    await ctx.send("Nothing else to unlock!")
                unlock_location_choice = await utils.create_select_menu(
                    self.bot, ctx, specific_unlockable_locations, "location", "choose", True
                )

                # Set the users location to where they unlocked, set it to be unlocked, and get rid of one of their unlocks. Send a response
                if type(unlock_location_choice) == str:
                    async with vbu.Database() as db:
                        await db("""UPDATE user_location_info SET current_location = $2 WHERE user_id = $1""", ctx.author.id, location)
                        await db("""UPDATE user_item_inventory SET new_location_unlock = new_location_unlock - 1 WHERE user_id = $1""", ctx.author.id)
                        await db(f"""UPDATE user_location_info SET {unlock_location_choice.replace(' ', '_').lower()}_unlocked = TRUE WHERE User_id = $1""", ctx.author.id)
                    await ctx.send(
                        f"Unlocked and traveled to {unlock_location_choice}!")
            elif chosen_button == 'close_menu':

                # Give a response and close the menu
                await chosen_button_payload.response.defer_update()
                menu_open = False

            # Get all the new data from after the user's last action and make a new embed with it
            async with vbu.Database() as db:
                user_locations_info = await utils.user_location_info_db_call(
                    ctx.author.id)
                user_item_inventory = await utils.user_item_inventory_db_call(ctx.author.id)
                location_pools_info = await utils.fish_pool_location_db_call()
            new_embed = discord.Embed(
                title=f"__{ctx.author.display_name}'s Fish Menu!__\n*Current Location: {user_locations_info[0]['current_location'].replace('_', ' ').title()}*")
            new_embed.set_image(
                url="https://cdn.discordapp.com/attachments/952006920858923060/1035613173274918912/fishing_idle.gif")
            for rarity, fish in FishSpecies.all_species_by_location_rarity[user_locations_info[0]['current_location']].items():
                rarity = rarity.upper()
                fish_in_rarity = []
                for single_fish in fish:
                    if user_locations_info[0][f"{single_fish.name}_caught"] > 0:
                        fish_in_rarity.append(
                            f"{single_fish.name.replace('_', ' ').title()} ({location_pools_info[0][f'{single_fish.name}_count']} Left)")
                    else:
                        fish_in_rarity.append(
                            f"??? ({location_pools_info[0][f'{single_fish.name}_count']} Left)\t")
                new_embed.add_field(name=rarity, value='\n'.join(
                    [f"{fish}" for fish in fish_in_rarity]), inline=True)
            if user_item_inventory[0]['new_location_unlock'] < 1:
                components.get_component('unlock').disable()
            effect_string = "** **"
            for effect in ["recycled_fishing_rod", "recycled_bait", "recycled_fish_hook", "recycled_fish_finder"]:
                amount = user_item_inventory[0][effect]
                formatted_effect = effect.replace("_", " ").title()
                if amount > 0:
                    effect_string += f"{formatted_effect}: {amount} casts left to apply to\n"
            new_embed.add_field(name="Effects", value=effect_string)
            await fish_menu_message.edit(embed=new_embed, components=components)

        # Disable components when the menu is exited
        await fish_menu_message.edit(components=components.disable_components())

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="old",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The fish or tank you want to rename"),
                discord.ApplicationCommandOption(
                    name="new",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The fish or tank's new name")]))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        This command renames a specified fish or tank.
        """

        # Get the user's data
        await utils.check_registered(self.bot, ctx, ctx.author.id)
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""",
                old,
                ctx.author.id,
            )
            tank_rows = await utils.user_tank_inventory_db_call(ctx.author.id)
            fish_rows = await utils.user_fish_inventory_db_call(ctx.author.id)

        spot_of_old = None
        if tank_rows:

            # If the old name is in tank rows, find the spot of it
            if old in tank_rows[0]["tank_name"]:
                for spot, tank in enumerate(tank_rows[0]["tank_name"]):
                    if old == tank:
                        spot_of_old = spot + 1

                    # If the new name matches any tanks return that they have a tank with that name
                    if new == tank:
                        return await ctx.send(
                            f"You already have a tank named **{new}**!",
                            allowed_mentions=discord.AllowedMentions.none(),
                        )

                # rename the tank in the database and make any fish in that tank in the new named tank
                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_tank_inventory SET tank_name[$3]=$1 WHERE user_id=$2;""",
                        new,
                        ctx.author.id,
                        spot_of_old,
                    )
                    await db(
                        """UPDATE user_fish_inventory SET tank_fish=$1 WHERE user_id = $2 AND tank_fish=$3""",
                        new,
                        ctx.author.id,
                        old,
                    )

                # Send confirmation message
                return await ctx.send(
                    f"{EMOJIS['aqua_love']}Congratulations, you have renamed **{old}** to **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Tell them if there is no fish or tank with the old name
        if not spot_of_old:
            if not fish_row:
                return await ctx.send(
                    f"{EMOJIS['aqua_shrug']}You have no fish or tank named **{old}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Check of fish is being changed to a name of a new fish
        for fish_name in fish_rows:
            if new == fish_name:
                return await ctx.send(
                    f"{EMOJIS['aqua_shrug']}You already have a fish named **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Update the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET fish_name=$1 WHERE user_id=$2 and fish_name=$3;""",
                new,
                ctx.author.id,
                old,
            )

        # Send confirmation message
        await ctx.send(
            f"{EMOJIS['aqua_love']}Congratulations, you have renamed **{old}** to **{new}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[discord.ApplicationCommandOption(
                name="crafted",
                type=discord.ApplicationCommandOptionType.string,
                description="The item you want to craft (leave blank for menu)",
                required=False)]))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def craft(self, ctx: commands.Context, *, crafted: str = None):
        '''
        Crafts inputted item, gives a list of what to craft and what it costs if not
        '''

        await utils.check_registered(self.bot, ctx, ctx.author.id)

        if crafted:
            crafted = crafted.title()

        if not crafted or crafted not in utils.items_required.keys():
            # Set up the menu for what is craftable and how much they cost
            embed = discord.Embed(title="Craftable Items")
            for craftable, needed in utils.items_required.items():
                crafting_menu_message = ""
                title = f"**{craftable}**"
                for item, amount in needed[0].items():
                    crafting_menu_message += f"\n{utils.EMOJIS['bar_empty']}{item.replace('_', ' ').title()}: {amount}"
                crafting_menu_message += f"\n{utils.EMOJIS['bar_empty']}{utils.EMOJIS['bar_empty']}{needed[1]}"
                embed.add_field(
                    name=title, value=crafting_menu_message, inline=False)
            embed.set_footer(
                text="Specify what you want to craft with \"craft [Item Name]\"")

            # If they don't enter a craftable item or don't enter anything give the craftable menu
            return await ctx.send(embed=embed)

        # If they enter one of the stacking items, check that they don't have the max
        amount = 1
        if crafted in ["Fishing Boots", "Trash Toys"]:
            async with vbu.Database() as db:
                amount_of_crafted = await db(f"""SELECT {crafted.replace(' ', '_').lower()} FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
            if amount_of_crafted[0][crafted.replace(' ', '_').lower()] == 5:
                return await ctx.send("You have the max amount of this item!")
        elif crafted in ["Recycled Fishing Rod", "Recycled Bait", "Recycled Waders"]:
            amount = 5
        # If they don't have the items to craft, let them know
        if not await utils.enough_to_craft(crafted, ctx.author.id):
            return await ctx.send("You do not have the required items to craft this.")

        async with vbu.Database() as db:

            # Get rid of the items taken to craft
            for item, required in utils.items_required[crafted][0].items():
                await db(f"""UPDATE user_item_inventory SET {item} = {item} - {required} WHERE user_id = $1""", ctx.author.id)

            db_crafted = crafted.replace(" ", "_").lower()

            # If they get a cast go to the user_balance table, else use the item inventory, and add 1 to the amount
            if db_crafted == "cast":
                await db(f"""UPDATE user_balance SET casts = casts + 1 WHERE user_id = $1""", ctx.author.id)
            else:
                await db(f"""UPDATE user_item_inventory SET {db_crafted} = {db_crafted} + $2 WHERE user_id = $1""", ctx.author.id, amount)

        # Let them know it was crafted
        return await ctx.send(f"{crafted} has been crafted!")


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
