from cogs.utils.fish_handler import DAYLIGHT_SAVINGS
from cogs.utils.misc_utils import seconds_converter
import random
from datetime import datetime as dt, timedelta

import voxelbotutils as vbu
import discord
from discord.ext import commands

from cogs import utils


class Fishing(vbu.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        super().__init__(bot)

    @vbu.command()
    @vbu.cooldown.cooldown(1, 15 * 60, commands.BucketType.user)
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
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
        async with self.bot.database() as db:
            upgrades = await db(
                """SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade, better_bait_upgrade, better_line_upgrade FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

            # no upgrades bro
            if not upgrades:
                upgrades = await db("""INSERT INTO user_upgrades (user_id) VALUES ($1) RETURNING *""", ctx.author.id)

        # Roll a dice to see if they caught multiple fish

        two_in_one_roll = random.randint(1, utils.LINE_UPGRADES[(upgrades[0]['line_upgrade'] + upgrades[0]['better_line_upgrade'])])
        if two_in_one_roll == 1:
            caught_fish = 2

        #
        for x in range(caught_fish):

            # See what our chances of getting each fish are
            rarity = random.choices(*utils.rarity_percentage_finder((upgrades[0]['bait_upgrade'] + upgrades[0]['better_bait_upgrade'])))[0]  # Chance of each rarity
            print(*utils.rarity_percentage_finder((upgrades[0]['bait_upgrade'] + upgrades[0]['better_bait_upgrade'])))
            print(rarity)
            special = random.choices(*utils.special_percentage_finder(upgrades[0]['lure_upgrade']))[0]  # Chance of modifier
            if special == "golden":
                special = "inverted"

            # See which fish they caught
            new_fish = random.choice(list(self.bot.fish[rarity].values())).copy()

            # See if we want to make the fish a modifier
            special_functions = {
                "inverted": utils.make_inverted(new_fish.copy()),
                "golden": utils.make_golden(new_fish.copy())
            }
            if special in special_functions:
                new_fish = special_functions[special]

            # Say how many of those fish they caught previously
            amount = 0
            a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
            async with self.bot.database() as db:
                user_inventory = await db("SELECT * FROM user_fish_inventory WHERE user_id=$1", ctx.author.id)

                # Achievements
                await db(
                    """INSERT INTO user_achievements (user_id, times_caught) VALUES ($1, 1)
                    ON CONFLICT (user_id) DO UPDATE SET times_caught = user_achievements.times_caught + 1""",
                    ctx.author.id,
                )
            for row in user_inventory:
                if row['fish'] == new_fish['raw_name']:
                    amount += 1

            # Tell the user about the fish they caught
            owned_unowned = "Owned" if amount > 0 else "Unowned"
            embed = discord.Embed(title=f"<:AquaFish:877939115948134442> You caught {a_an} *{rarity}* {new_fish['size']} **{new_fish['name']}**!")
            embed.add_field(name=owned_unowned, value=f"You have {amount} **{new_fish['name']}**", inline=False)
            embed.set_image(url="attachment://new_fish.png")
            embed.color = utils.RARITY_CULERS[rarity]
            fish_file = discord.File(new_fish["image"], "new_fish.png")


            # Ask if they want to sell the fish they just caught
            print(utils.current_fishers)
            await utils.ask_to_sell_fish(self.bot, ctx, new_fish, embed=embed, file=fish_file)

        # And now they should be allowed to fish again
        utils.current_fishers.remove(ctx.author.id)
        print(utils.current_fishers)

    @fish.error
    async def fish_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = timedelta(seconds=int(error.retry_after))

        await ctx.send(f'The fish are scared, please try again {vbu.TimeFormatter(dt.utcnow() + time - timedelta(hours=DAYLIGHT_SAVINGS)).relative_time}.')

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        This command renames a specified fish or tank.
        """

        # Get the user's fish inventory based on the fish's name
        async with self.bot.database() as db:
            fish_row = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""", old, ctx.author.id)
            tank_rows = await db("""SELECT tank_name FROM user_tank_inventory WHERE user_id=$1""", ctx.author.id)
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE user_id=$1""", ctx.author.id)

        # Check if the user doesn't have the fish

        spot_of_old = None
        print(tank_rows)
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
                async with self.bot.database() as db:
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
        async with self.bot.database() as db:
            await db(
                """UPDATE user_fish_inventory SET fish_name=$1 WHERE user_id=$2 and fish_name=$3;""",
                new, ctx.author.id, old,
            )

        # Send confirmation message
        await ctx.send(
            f"Congratulations, you have renamed **{old}** to **{new}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def skin(self, ctx: commands.Context, skin: str, *, fish: str):
        '''
        Applies a skin to a fish you own
        '''
    @vbu.command()
    @vbu.bot_has_permissions(send_messages=True, embed_links=True)
    async def preview(self, ctx: commands.Context, type: str, *, skin: str):
        '''
        Previews a skin
        '''



def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
