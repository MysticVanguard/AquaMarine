import random
import math
import asyncio
from PIL.Image import new
import discord
from discord.ext import commands, tasks, vbu
import string

from cogs import utils
from cogs.utils import EMOJIS


class Fishing(vbu.Cog):

    # Start the loop when the cog is started
    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.user_cast_loop.start()

    # When the cog is turned off, turn the loop off
    def cog_unload(self):
        self.user_cast_loop.cancel()

    # Every hour, everyone gets a cast
    @tasks.loop(hours=1)
    async def user_cast_loop(self):
        async with vbu.Database() as db:
            casts = await db("""SELECT * FROM user_balance""")
            for x in casts:
                if x["casts"] >= 50:
                    continue
                await db(
                    """UPDATE user_balance SET casts=casts+1 WHERE user_id = $1""",
                    x["user_id"],
                )

    # Wait until the bot is on and ready and not just until the cog is on
    @user_cast_loop.before_loop
    async def before_user_cast_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        This command catches a fish.
        """

        # Add their id to a list to make sure they can't fish twice
        if ctx.author.id in utils.current_fishers:
            return await ctx.send(
                f"**{ctx.author.display_name}**, you're already fishing!"
            )
        utils.current_fishers.append(ctx.author.id)

        # Fetch their upgrades and casts, if they arent in the database yet add them to it with 6 starting casts
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade, crate_chance_upgrade, crate_tier_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            casts = await db(
                """SELECT casts FROM user_balance WHERE user_id = $1""",
                ctx.author.id,
            )
            if not upgrades:
                upgrades = await db(
                    """INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""",
                    ctx.author.id,
                )
            if not casts:
                casts = await db(
                    """INSERT INTO user_balance (user_id, casts) VALUES ($1, 6) RETURNING casts""",
                    ctx.author.id,
                )

        # If they have no casts tell them they can't fish and remove them from currrent fishers
        if casts[0]["casts"] <= 0:
            utils.current_fishers.remove(ctx.author.id)
            return await ctx.send(
                "You have no casts, please wait atleast an hour until the next casts are out."
            )

        # pick a random number using the line upgrade, if it is equal to 1 they get to fish twice
        caught_fish = 1
        two_in_one_roll = random.randint(
            1, utils.LINE_UPGRADES[upgrades[0]["line_upgrade"]]
        )
        if two_in_one_roll == 1:
            caught_fish = 2
        # For each fish caught...
        for _ in range(caught_fish):

            # Use upgrades for chances of rarity and mutation, and choose one with weighted randomness
            rarity = random.choices(
                *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
            )[0]
            special = random.choices(
                *utils.special_percentage_finder(upgrades[0]["lure_upgrade"])
            )[0]
            # Disable golden for now...
            if special == "golden":
                special = "inverted"

            # See which fish they caught by taking a random fish from the chosen rarity
            new_fish = random.choice(
                list(self.bot.fish[rarity].values())
            ).copy()
            while new_fish["raw_name"] in utils.past_fish:
                new_fish = random.choice(
                    list(self.bot.fish[rarity].values())
                ).copy()
            # See if we want to make the fish mutated based on what the modifier is
            special_functions = {
                "inverted": utils.make_inverted(new_fish.copy()),
                "golden": utils.make_golden(new_fish.copy()),
            }
            if special in special_functions:
                new_fish = special_functions[special]

            # Grammar
            a_an = (
                "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
            )

            # Get their fish inventory, add 1 to their times caught in achievements, subtract 1 from their casts
            async with vbu.Database() as db:
                user_inventory = await db(
                    "SELECT * FROM user_fish_inventory WHERE user_id=$1",
                    ctx.author.id,
                )

                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                    ctx.author.id,
                )
                await db(
                    """UPDATE user_balance SET casts = casts-1 WHERE user_id = $1""",
                    ctx.author.id,
                )

            # Find out how many of those fish they caught previously
            amount = 0
            for row in user_inventory:
                if row["fish"] == new_fish["raw_name"]:
                    amount += 1

            # Set the fish file to the fishes image
            fish_file = discord.File(new_fish["image"], "new_fish.png")
            choices = [new_fish['name']]
            for i in range(3):
                random_rarity = random.choices(
                    *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                )[0]
                random_fish = random.choice(
                    list(self.bot.fish[random_rarity].values())
                ).copy()
                while random_fish['name'] in choices:
                    random_rarity = random.choices(
                        *utils.rarity_percentage_finder(upgrades[0]["bait_upgrade"])
                    )[0]
                    random_fish = random.choice(
                        list(self.bot.fish[random_rarity].values())
                    ).copy()
                choices.append(random_fish['name'])

            random.shuffle(choices)

            # And send the message
            components = discord.ui.MessageComponents(
                discord.ui.ActionRow(
                    discord.ui.Button(
                        label=choices[0], custom_id=choices[0]
                    ),
                    discord.ui.Button(
                        label=choices[1], custom_id=choices[1]
                    ),
                    discord.ui.Button(
                        label=choices[2], custom_id=choices[2]
                    ),
                    discord.ui.Button(
                        label=choices[3], custom_id=choices[3]
                    ),
                ),
            )

            guess_message = await ctx.send("Guess the name of this fish:", file=fish_file, components=components)

            # Make the button check
            def button_check(payload):
                if payload.message.id != guess_message.id:
                    return False
                self.bot.loop.create_task(payload.response.defer_update())
                return payload.user.id == ctx.author.id

            # Wait for them to click a button
            try:
                chosen_button_payload = await self.bot.wait_for(
                    "component_interaction", timeout=60.0, check=button_check
                )
                chosen_button = (
                    chosen_button_payload.component.custom_id
                )
            except asyncio.TimeoutError:
                await guess_message.edit(
                    components=components.disable_components()
                )
                await ctx.send("Timed out asking for guess.")
                chosen_button = "AAAAAAAAAAAAAA"

            # Give them a bonus based on the fish's cost and tell them they got it correct if they did

            if chosen_button == new_fish["name"]:
                bonus = 15 + math.floor(int(new_fish["cost"]) / 10)
                await ctx.channel.send(
                    f"<@{ctx.author.id}> guessed correctly and recieved {bonus} bonus sand dollars {EMOJIS['sand_dollar']}!"
                )

                # Update the users balance with the bonus
                async with vbu.Database() as db:
                    await db(
                        """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                        ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                        ctx.author.id,
                        bonus,
                    )

            # Else tell them it was wrong
            else:
                await ctx.channel.send(
                    f"Incorrect <@{ctx.author.id}>, no bonus given."
                )

            # Tell the user about the fish they caught
            owned_unowned = "Owned" if amount > 0 else "Unowned"
            embed = discord.Embed(
                title=f"{EMOJIS['aqua_fish']} {ctx.author.display_name} caught {a_an} *{rarity}* {new_fish['size']} **{new_fish['name']}**!"
            )
            embed.add_field(
                name=owned_unowned,
                value=f"You have {amount} **{new_fish['name']}**",
                inline=False,
            )
            embed.set_image(url="attachment://new_fish.png")
            embed.color = utils.RARITY_CULERS[rarity]

            # Ask if they want to sell the fish they just caught or keep it
            await utils.ask_to_sell_fish(self.bot, ctx, new_fish, embed=embed)

        # Find if they catch a crate with the crate_chance_upgrade
        crate_catch = random.randint(
            1, utils.CRATE_CHANCE_UPGRADE[upgrades[0]["crate_chance_upgrade"]]
        )
        # If they caught it...
        if crate_catch == 1:
            crate_loot = []

            # Choose a random crate tier based on their crate_tier_upgrade and add the loot for that tier
            crate = random.choices(
                (
                    "Wooden",
                    "Bronze",
                    "Steel",
                    "Golden",
                    "Diamond",
                    "Enchanted",
                ),
                utils.CRATE_TIER_UPGRADE[upgrades[0]["crate_tier_upgrade"]],
            )
            crate_loot.append(
                (
                    "balance",
                    random.randint(0, utils.CRATE_TIERS[crate[0]][0]),
                    "user_balance",
                )
            )
            crate_loot.append(
                (
                    "casts",
                    random.randint(0, utils.CRATE_TIERS[crate[0]][1]),
                    "user_balance",
                )
            )
            crate_loot.append(
                (
                    random.choices(
                        ("none", "cfb", "ufb", "rfb", "ifb", "hlfb"),
                        utils.CRATE_TIERS[crate[0]][2],
                    )[0],
                    random.randint(0, utils.CRATE_TIERS[crate[0]][3]),
                    "user_inventory",
                )
            )
            crate_loot.append(
                (
                    random.choices(
                        ("none", "flakes", "pellets", "wafers"),
                        utils.CRATE_TIERS[crate[0]][4],
                    )[0],
                    random.randint(0, utils.CRATE_TIERS[crate[0]][5]),
                    "user_inventory",
                )
            )
            crate_loot.append(
                (
                    random.choices(
                        ("none", "fullness", "experience", "mutation"),
                        utils.CRATE_TIERS[crate[0]][6],
                    )[0],
                    random.randint(0, utils.CRATE_TIERS[crate[0]][7]),
                    "user_inventory",
                )
            )

            # Initialize variables and display variable for every item
            crate_message = ""
            nl = "\n"
            display = {
                "balance": "Sand Dollars",
                "casts": "Casts",
                "cfb": "Common Fish Bags",
                "ufb": "Uncommon Fish Bags",
                "rfb": "Rare Fish Bags",
                "ifb": "Inverted Fish Bags",
                "hlfb": "High Level Fish Bags",
                "flakes": "Fish Flakes",
                "pellets": "Fish Pellets",
                "wafers": "Fish Wafers",
                "experience": "Experience Potions",
                "mutation": "Mutation Potions",
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
                            """INSERT INTO {0} (user_id, {1}) VALUES ($1, $2)
                                    ON CONFLICT (user_id) DO UPDATE SET {1} = {0}.{1} + $2""".format(
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

        # And now they should be allowed to fish again
        utils.current_fishers.remove(ctx.author.id)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        This command renames a specified fish or tank.
        """

        # Get the user's fish with the old name, all their fish, and all their tanks
        async with vbu.Database() as db:
            fish_row = await db(
                """SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""",
                old,
                ctx.author.id,
            )
            tank_rows = await db(
                """SELECT tank_name FROM user_tank_inventory WHERE user_id=$1""",
                ctx.author.id,
            )
            fish_rows = await db(
                """SELECT fish_name FROM user_fish_inventory WHERE user_id=$1""",
                ctx.author.id,
            )

        # Finds if you're renaming a tank
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
                    f"Congratulations, you have renamed **{old}** to **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )
        # Tell them if there is no fish or tank with the old name
        if not spot_of_old:
            if not fish_row:
                return await ctx.send(
                    f"You have no fish or tank named **{old}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        # Check of fish is being changed to a name of a new fish
        for fish_name in fish_rows:
            if new == fish_name:
                return await ctx.send(
                    f"You already have a fish named **{new}**!",
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
            f"Congratulations, you have renamed **{old}** to **{new}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
