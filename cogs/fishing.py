import random
from datetime import datetime as dt, timedelta

import math
import asyncio
import discord
from discord.ext import commands, tasks, vbu

from cogs import utils
from cogs.utils.fish_handler import DAYLIGHT_SAVINGS


class Fishing(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.user_cast_loop.start()

    def cog_unload(self):
        self.user_cast_loop.cancel()

    @tasks.loop(hours=1)
    async def user_cast_loop(self):
        async with vbu.Database() as db:
            await db("""UPDATE user_balance SET casts=casts+1""")

    @user_cast_loop.before_loop
    async def before_user_cast_loop(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.cooldown(1, 10 * 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        This command catches a fish.
        """

        # Make sure they can't fish twice
        if ctx.author.id in utils.current_fishers:
            return await ctx.send(f"**{ctx.author.display_name}**, you're already fishing!")
        utils.current_fishers.append(ctx.author.id)
        caught_fish = 1

        # Upgrades be like
        async with vbu.Database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            casts = await db(
                """SELECT casts FROM user_balance WHERE user_id = $1""",
                ctx.author.id
            )

            # no upgrades bro
            if not upgrades:
                upgrades = await db("""INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""", ctx.author.id)
            if not casts:
                casts = await db("""INSERT INTO user_balance (user_id, casts) VALUES ($1, 6) RETURNING casts""", ctx.author.id)

        if casts[0]['casts'] <= 0:
            utils.current_fishers.remove(ctx.author.id)
            return await ctx.send("You have no casts, please wait atleast an hour until the next casts are out.")

        # Roll a dice to see if they caught multiple fish
        two_in_one_roll = random.randint(
            1, utils.LINE_UPGRADES[upgrades[0]['line_upgrade']])
        if two_in_one_roll == 1:
            caught_fish = 2

        #
        for _ in range(caught_fish):

            # See what our chances of getting each fish are
            # Chance of each rarity
            rarity = random.choices(
                *utils.rarity_percentage_finder(upgrades[0]['bait_upgrade']))[0]
            print(*utils.rarity_percentage_finder(upgrades[0]['bait_upgrade']))
            special = random.choices(
                *utils.special_percentage_finder(upgrades[0]['lure_upgrade']))[0]  # Chance of modifier
            if special == "golden":
                special = "inverted"

            # See which fish they caught
            new_fish = random.choice(
                list(self.bot.fish[rarity].values())).copy()

            # See if we want to make the fish a modifier
            special_functions = {
                "inverted": utils.make_inverted(new_fish.copy()),
                "golden": utils.make_golden(new_fish.copy())
            }
            if special in special_functions:
                new_fish = special_functions[special]

            # Say how many of those fish they caught previously
            amount = 0
            a_an = "an" if rarity[0].lower() in (
                "a", "e", "i", "o", "u") else "a"
            async with vbu.Database() as db:
                user_inventory = await db("SELECT * FROM user_fish_inventory WHERE user_id=$1", ctx.author.id)

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
            for row in user_inventory:
                if row['fish'] == new_fish['raw_name']:
                    amount += 1

            fish_file = discord.File(new_fish["image"], "new_fish.png")
            await ctx.send(f"Guess the name of this fish", file=fish_file)
            def check(
                guess): return guess.author == ctx.author and guess.channel == ctx.channel
            try:
                message_given = await ctx.bot.wait_for("message", timeout=60.0, check=check)
                message = message_given.content
                if message.title() == new_fish['name']:
                    bonus = 10 + math.floor(int(new_fish['cost']) / 20)
                    await ctx.send(f"You guessed correctly and recieved {bonus} bonus sand dollars <:sand_dollar:877646167494762586>!")
                    async with vbu.Database() as db:
                        await db(
                            """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                            ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                            ctx.author.id, bonus
                        )
                else:
                    await ctx.send(f"Incorrect, no bonus given.")
            except asyncio.TimeoutError:
                await ctx.send("Timed out asking for guess.")
                return False

            # Tell the user about the fish they caught
            owned_unowned = "Owned" if amount > 0 else "Unowned"
            embed = discord.Embed(
                title=f"<:AquaFish:877939115948134442> You caught {a_an} *{rarity}* {new_fish['size']} **{new_fish['name']}**!")
            embed.add_field(
                name=owned_unowned, value=f"You have {amount} **{new_fish['name']}**", inline=False)
            embed.set_image(url="attachment://new_fish.png")
            embed.color = utils.RARITY_CULERS[rarity]

            # Ask if they want to sell the fish they just caught
            print(utils.current_fishers)
            await utils.ask_to_sell_fish(self.bot, ctx, new_fish, embed=embed)

        # CRATE_CHANCE_UPGRADE = {0: 8760, 1: 6480, 2: 4320, 3: 2160, 4: 1440, 5: 720}

        # CRATE_TIERS = {
        #     "Wooden": (500, 1, (1.0, 0, 0, 0, 0, 0), 1, (1.0, 0, 0, 0), 1, (1.0, 0, 0, 0), 1),
        #     "Bronze": (1000, 2, (.89, .1, .01, 0, 0, 0), 2, (.89, .1, .01, 0), 2, (.89, .1, .01, 0), 1),
        #     "Steel": (2500, 5, (.74, .2, .05, .01, 0, 0), 4, (.74, .2, .05, .01), 4, (.74, .2, .05, .01), 1),
        #     "Golden": (5000, 10, (.54, .3, .1, .05, .01, 0), 7, (.54, .3, .1, .05), 7, (.54, .3, .1, .05), 2),
        #     "Diamond": (10000, 20, (.29, .4, .15, .1, .05, .01), 11, (.29, .4, .15, .1), 11, (.29, .4, .15, .1), 2),
        #     "Enchanted": (50000, 100, (0, .5, .2, .15, .1, 0.05), 16, (0, .5, .2, .15), 16, (0, .5, .2, .15), 3),
        # }
        # CRATE_TIER_UPGRADE = {
        #     0: (1.0, 0, 0, 0, 0, 0),
        #     1: (.89, .1, .01, 0, 0, 0),
        #     2: (.74, .2, .05, .01, 0, 0),
        #     3: (.54, .3, .1, .05, .01, 0),
        #     4: (.29, .4, .15, .1, .05, .01),
        #     5: (0, .5, .2, .15, .1, 0.05)
        # }

        crate_catch = random.randint(
            1, utils.CRATE_CHANCE_UPGRADE[upgrades['crate_chance_upgrade']])
        if crate_catch == 1:
            crate_loot = []
            crate = random.choices(
                ("Wooden", "Bronze", "Steel", "Golden", "Diamond", "Enchanted"), utils.CRATE_TIER_UPGRADE[upgrades['crate_tier_upgrade']])
            crate_loot.append(("balance", random.randint(
                0, utils.CRATE_TIERS[crate[0]][0]), "user_balance"))
            crate_loot.append(("casts", random.randint(
                0, utils.CRATE_TIERS[crate[0]][1]), "user_balance"))
            crate_loot.append((random.choices(("none", "cfb", "ufb", "rfb", "ifb", "hlfb"),
                                              utils.CRATE_TIERS[crate[0]][2])[0], random.randint(0, utils.CRATE_TIERS[crate[0]][3]), "user_inventory"))
            crate_loot.append((random.choices(("none", "flakes", "pellets", "wafers"),
                                              utils.CRATE_TIERS[crate[0]][4])[0], random.randint(0, utils.CRATE_TIERS[crate[0]][5]), "user_inventory"))
            crate_loot.append((random.choices(("none", "fullness", "experience", "mutation"),
                                              utils.CRATE_TIERS[crate[0]][6])[0], random.randint(0, utils.CRATE_TIERS[crate[0]][7]), "user_inventory"))

            crate_message = ""
            nl = "\n"
            display = {"balance": "Sand Dollars", "casts": "Casts", "cfb": "Common Fish Bags",
                       "ufb": "Uncommon Fish Bags", "rfb": "Rare Fish Bags", "ifb": "Inverted Fish Bags",
                       "hlfb": "High Level Fish Bags", "flakes": "Fish Flakes", "pellets": "Fish Pellets",
                       "wafers": "Fish Wafers", "experience": "Experience Potions", "mutation": "Mutation Potions",
                       "fullness": "Fullness Potions"
                       }
            for data in crate_loot:
                print(data)
                type_of_loot, amount_of_loot, table_of_loot = data
                if type_of_loot != "none" and amount_of_loot != 0:
                    await db(
                        """INSERT INTO {0} (user_id, {1}) VALUES ($1, $2)
                            ON CONFLICT (user_id) DO UPDATE SET {1} = {0}.{1} + $2""".format(table_of_loot, type_of_loot),
                        ctx.author.id, amount_of_loot
                    )
                    crate_message += f"{nl}{amount_of_loot}x {display[type_of_loot]} recieved!"

            await ctx.send(f"You caught a {crate[0]} crate containing: {crate_message}")

        # And now they should be allowed to fish again
        utils.current_fishers.remove(ctx.author.id)
        print(utils.current_fishers)

    @fish.error
    async def fish_error(self, ctx: commands.Context, error: commands.CommandError):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))
        relative_time = discord.utils.format_dt(
            dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS), style="R")
        await ctx.send(f'The fish are scared, please try again {relative_time}.')

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        This command renames a specified fish or tank.
        """

        # Get the user's fish inventory based on the fish's name
        async with vbu.Database() as db:
            fish_row = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""", old, ctx.author.id)
            tank_rows = await db("""SELECT tank_name FROM user_tank_inventory WHERE user_id=$1""", ctx.author.id)
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE user_id=$1""", ctx.author.id)

        # Check if the user doesn't have the fish
        spot_of_old = None
        if tank_rows:
            if old in tank_rows[0]['tank_name']:

                for spot, tank in enumerate(tank_rows[0]['tank_name']):
                    if old == tank:
                        spot_of_old = spot + 1
                    if new == tank:
                        return await ctx.send(
                            f"You already have a tank named **{new}**!",
                            allowed_mentions=discord.AllowedMentions.none()
                        )

                async with vbu.Database() as db:
                    await db(
                        """UPDATE user_tank_inventory SET tank_name[$3]=$1 WHERE user_id=$2;""",
                        new, ctx.author.id, spot_of_old,
                    )
                    await db(
                        """UPDATE user_fish_inventory SET tank_fish=$1 WHERE user_id = $2 AND tank_fish=$3""",
                        new, ctx.author.id, old
                    )

                # Send confirmation message
                return await ctx.send(
                    f"Congratulations, you have renamed **{old}** to **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none(),
                )

        if not spot_of_old:
            if not fish_row:
                return await ctx.send(
                    f"You have no fish or tank named **{old}**!",
                    allowed_mentions=discord.AllowedMentions.none()
                )

        # Check of fish is being changed to a name of a new fish
        for fish_name in fish_rows:
            if new == fish_name:
                return await ctx.send(
                    f"You already have a fish named **{new}**!",
                    allowed_mentions=discord.AllowedMentions.none()
                )

        # Update the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_fish_inventory SET fish_name=$1 WHERE user_id=$2 and fish_name=$3;""",
                new, ctx.author.id, old,
            )

        # Send confirmation message
        await ctx.send(
            f"Congratulations, you have renamed **{old}** to **{new}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(enabled=False)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def skin(self, ctx: commands.Context, skin: str, *, fish: str):
        """
        Applies a skin to a fish you own
        """

        ...

    @commands.command(enabled=False)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def preview(self, ctx: commands.Context, type: str, *, skin: str):
        """
        Previews a skin
        """

        ...


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
