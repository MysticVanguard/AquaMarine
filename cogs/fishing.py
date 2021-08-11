import random

import re
import asyncio
import voxelbotutils as vbu

import discord
from discord.ext import commands

from cogs import utils

class Fishing(vbu.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.current_fishers = []

    @vbu.command(aliases=["bucket", "fb"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True)
    async def fishbucket(self, ctx: commands.Context, user: discord.User = None):
        """
        This command checks your fish bucket or another users.
        """

        # Default the user to the author of the command
        user = user or ctx.author

        async with self.bot.database() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1 AND tank_fish=''""", user.id)

        if not fish_rows:
            return await ctx.send("You have no fish in your bucket!" if user == ctx.author else f"{user.display_name} has no fish in their bucket!")

        # totalpages = len(fetched) // 5 + (len(fetched) % 5 > 0)
        # if page < 1 or page > totalpages:
        #     return await ctx.send("That page is doesn't exist.")

        embed = discord.Embed()
        embed.title = f"{user.display_name}'s Fish Bucket"

        fish_list = [(i['fish_name'], i['fish']) for i in fish_rows]  # List of tuples (Fish Name, Fish Type)
        fish_list = sorted(fish_list, key=lambda x: x[1])

        fields = []  # The "pages" that the user can scroll through are the different rarity levels

        sorted_fish = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": [],
            "legendary": [],
            "mythic": []
        }

        # Sorted Fish will become a dictionary of {rarity: [list of fish names of fish in that category]} if the fish is in the user's inventory
        for rarity, fish_types in self.bot.fish.items():  # For each rarity level
            for _, fish_detail in fish_types.items():  # For each fish in that level
                raw_name = fish_detail["raw_name"]
                for user_fish_name, user_fish in fish_list:
                    if raw_name == utils.get_normal_name(user_fish):  # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        sorted_fish[rarity].append((user_fish_name, user_fish, fish_detail['size']))  # Append to the dictionary

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}** ({fish_size.title()})" for fish_name, fish_type, fish_size in fish_list]
                field = (rarity.title(), "\n".join(fish_string))
                [fields.append(i) for i in utils.get_fixed_field(field)]

        # Create an embed
        await utils.paginate(ctx, fields, user)

    @vbu.command()
    @vbu.cooldown.cooldown(1, 30 * 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        This command catches a fish.
        """

        # Make sure they can't fish twice
        if ctx.author.id in self.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        self.current_fishers.append(ctx.author.id)
        catches = 1

        #upgrades be like
        async with self.bot.database() as db:
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
            if not upgrades:
                await db("""INSERT INTO user_upgrades (user_id) VALUES ($1)""", ctx.author.id)
                upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
        two_in_one_chance = { 1: (1, 500), 2: (1, 400), 3: (1, 300), 4: (1, 200), 5: (1, 100)}
        two_in_one_roll = random.randint(two_in_one_chance[upgrades[0]['line_upgrade']][0], two_in_one_chance[upgrades[0]['line_upgrade']][1])
        if two_in_one_roll == 1:
            catches = 2
        for x in range(catches):
            # See what our chances of getting each fish are
            # print(utils.rarity_percentage_finder(upgrades[0]['bait_upgrade']))
            rarity = random.choices(*utils.rarity_percentage_finder(upgrades[0]['bait_upgrade']))[0]  # Chance of each rarity
            special = random.choices(*utils.special_percentage_finder(upgrades[0]['lure_upgrade']))[0]  # Chance of modifier

            # See which fish they caught
            new_fish = random.choice(list(self.bot.fish[rarity].values())).copy()

            special_functions = {
                "inverted": utils.make_inverted(new_fish.copy()),
                "golden": utils.make_golden(new_fish.copy())
            }

            if special in special_functions.keys():
                new_fish = special_functions[special]

            # Say how many of those fish they caught previously
            amount = 0
            a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
            async with self.bot.database() as db:
                user_inventory = await db("SELECT * FROM user_fish_inventory WHERE user_id=$1", ctx.author.id)
            for row in user_inventory:
                if row['fish'] == new_fish['raw_name']:
                    amount = amount + 1

            owned_unowned = "Owned" if amount > 0 else "Unowned"
            # Tell the user about the fish they caught
            embed = discord.Embed()
            embed.title = f"You caught {a_an} {rarity} {new_fish['size']} {new_fish['name']}!"
            embed.add_field(name=owned_unowned, value=f"You have {amount} {new_fish['name']}", inline=False)
            embed.set_image(url="attachment://new_fish.png")
            embed.color = utils.RARITY_CULERS[rarity]
            fish_file = discord.File(new_fish["image"], "new_fish.png")
            message = await ctx.send(file=fish_file, embed=embed)

            # Ask if they want to sell the fish they just caught
            await utils.ask_to_sell_fish(self.bot, ctx.author, message, new_fish)

        # And now they should be allowed to fish again
        self.current_fishers.remove(ctx.author.id)

    @fish.error
    async def fish_error(self, ctx, error):

        # Only handle cooldown errors
        if not isinstance(error, commands.CommandOnCooldown):
            raise error

        time = error.retry_after
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
        await ctx.send(f'The fish are scared, please try again in {round(time)} {form}.')

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        Renames specified fish.
        """

        # Get the user's fish inventory based on the fish's name
        async with self.bot.database() as db:
            fish_row = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2;""", old, ctx.author.id)
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE user_id=$2;""", ctx.author.id)

        # Check if the user doesn't have the fish
        if not fish_row:
            return await ctx.send(
                f"You have no fish named {old}!",
                allowed_mentions=discord.AllowedMentions.none()
            )

        # Check of fish is being changed to a name of a new fish
        for fish_name in fish_rows['fish_name']:
            if new == fish_name:
                return await ctx.send(
                    f"You already have a fish named {new}!",
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
            f"Congratulations, you have renamed {old} to {new}!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def release(self, ctx: commands.Context, name: str):
        """
        Releases specified fish back into the wild.
        """

        # Get the user's fish inventory based on the fish's name
        async with self.bot.database() as db:
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2;""", name, ctx.author.id)

        # Check if the user has the fish
        if fish_rows:

            # Update the database
            async with self.bot.database() as db:
                await db(
                    """DELETE FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2""",
                    name, ctx.author.id,
                )

            # Send confirmation message
            return await ctx.send(
                f"Goodbye {name}!",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        await ctx.send(
                f"You have no fish named {name}!",
                allowed_mentions=discord.AllowedMentions.none(),
            )


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
