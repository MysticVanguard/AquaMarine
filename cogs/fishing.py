import random

import re
import asyncio

import discord
from discord.ext import commands

import utils


class Fishing(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.current_fishers = []

    async def ask_to_sell_fish(self, user: discord.User, message: discord.Message, new_fish: dict):
        """
        Ask the user if they want to sell a fish they've been given.
        """

        # Add the emojis to the message
        emojis = [844594468580491264, 844594478392147968]
        for i in emojis:
            await message.add_reaction(self.bot.get_emoji(i))

        # See what reaction the user is adding to the message
        check = lambda reaction, reactor: reaction.emoji.id in emojis and reactor.id == user.id and reaction.message.id == message.id
        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            choice = "sell" if reaction.emoji.id == 844594478392147968 else "keep"
        except asyncio.TimeoutError:
            await message.channel.send("Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
            choice = "sell"

        # See if they want to sell the fish
        if choice == "sell":
            async with utils.DatabaseConnection() as db:
                await db(
                    """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                    user.id, int(new_fish["cost"]),
                )
            await message.channel.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}** Sand Dollars <:sand_dollar:852057443503964201>!")
            return

        
        # Get their current fish names
        fish_names = []

        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id=$1""", user.id)
        fish_names = [i['fish_name'] for i in fish_rows]
        fish_list = [(i['fish_name'], i['fish']) for i in fish_rows]
        fish_list = sorted(fish_list, key=lambda x: x[1])
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
                    if raw_name == self.get_normal_name(user_fish):  # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        sorted_fish[rarity].append((user_fish_name, user_fish))  # Append to the dictionary

        for rarity in sorted_fish:
            if rarity == new_fish['rarity']:
                if len(sorted_fish[rarity]) >= 10:
                    async with utils.DatabaseConnection() as db:
                        await db(
                            """INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                            ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2""",
                            user.id, int(new_fish["cost"]),
                        )
                    await message.channel.send(f"You have the max amount of fish in your fish bucket for that rarity (10). Sold your **{new_fish['name']}** for **{new_fish['cost']}** Sand Dollars <:sand_dollar:852057443503964201>!")
                    return
        # They want to keep - ask what they want to name the fish
        await message.channel.send("What do you want to name your new fish? (32 character limit and cannot be named the same as another fish you own)")
        check = lambda m: m.author == user and m.channel == message.channel and len(m.content) > 1 and len(m.content) <= 32 and m.content not in fish_names
        try:
            name_message = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name_message.content
            await message.channel.send(f"Your new fish **{name}** has been added to your bucket!")
        except asyncio.TimeoutError:
            name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
            await message.channel.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")

        # Save the fish name
        async with utils.DatabaseConnection() as db:
            await db(
                """INSERT INTO user_fish_inventory (user_id, fish, fish_name, fish_size) VALUES ($1, $2, $3, $4)""",
                user.id, new_fish["raw_name"], name, new_fish["size"]
            )


    @commands.command(aliases=["bucket", "fb"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True, manage_messages=True)
    async def fishbucket(self, ctx: commands.Context, user: discord.User = None):
        """
        `a.fishbucket \"user(optional)\"` This command checks your fish bucket or another users. A user can only have ten max in each rarity in their fish bucket, but fish buckets don\'t include your deposited fish.
        """

        # Default the user to the author of the command
        user = user or ctx.author

        async with utils.DatabaseConnection() as db:
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
                    if raw_name == self.get_normal_name(user_fish):  # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        sorted_fish[rarity].append((user_fish_name, user_fish))  # Append to the dictionary

        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}**" for fish_name, fish_type in fish_list]
                field = (rarity.title(), "\n".join(fish_string))
                [fields.append(i) for i in self.get_fixed_field(field)]

        # Create an embed
        curr_index = 1
        curr_field = fields[curr_index - 1]
        embed = self.create_bucket_embed(user, curr_field)

        fish_message = await ctx.send(embed=embed)

        valid_reactions = ["◀️", "▶️", "⏹️", "🔢"]
        [await fish_message.add_reaction(reaction) for reaction in valid_reactions]  # Add the pagination reactions to the message

        def reaction_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions and reaction.message == fish_message

        while True:  # Keep paginating until the user clicks stop
            try:
                chosen_reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                chosen_reaction = chosen_reaction.emoji
            except asyncio.TimeoutError:
                chosen_reaction = "⏹️"
            
            index_chooser = {
                "◀️": max(1, curr_index - 1),
                "▶️": min(len(fields), curr_index + 1)
            }
            
            if chosen_reaction in index_chooser.keys():
                curr_index = index_chooser[chosen_reaction]  # Keep the index in bounds
                curr_field = fields[curr_index - 1]

                await fish_message.edit(embed=self.create_bucket_embed(user, curr_field))

            elif chosen_reaction == "⏹️":
                await fish_message.clear_reactions()
                break  # End the while loop

            elif chosen_reaction == "🔢":
                number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")

                # Check for custom message
                def message_check(message):
                    return message.author == ctx.author and message.channel == fish_message.channel and message.content.isdigit()

                user_message = await self.bot.wait_for('message', check=message_check)
                user_input = int(user_message.content)

                curr_index = min(len(fields), max(1, user_input))
                curr_field = fields[curr_index - 1]

                await fish_message.edit(embed=self.create_bucket_embed(user, curr_field))
                await number_message.delete()
                await user_message.delete()

    def create_bucket_embed(self, user, field):
        """
        Creates the embed for the pagination page for the fishbucket
        """
        embed = discord.Embed()  # Create a new embed to edit the message
        embed.title = f"**{user.display_name}'s Fish Bucket**\n"
        embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
        return embed

    def get_normal_name(self, fish_name):
        """
        Get the non-inverted/golden name for the fish
        """
        match = re.match(r"(inverted_|golden_)(?P<fish_name>.*)", fish_name)
        if match:
            return match.group("fish_name")
        return fish_name
        
    def get_fixed_field(self, field):
        """
        Return a list of tuples for the rarity-level in the pagination to fix fields that are too large
        """
        fish_string_split = field[1].split('\n')
        fixed_field = []
        current_string = ""
        fish_character_sum = 0

        for index, fish_string in enumerate(fish_string_split):
            fish_character_sum += len("\n" + fish_string)
            if fish_character_sum < 1020:
                current_string += "\n" + fish_string
                if index == len(fish_string_split) - 1:
                    fixed_field.append((field[0], current_string))
            else:
                fixed_field.append((field[0], current_string))
                current_string = fish_string
                fish_character_sum = 0
            
        if not fixed_field:
            fixed_field = [field]

        return fixed_field

    @commands.command()
    @commands.cooldown(1, 30 * 60, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx: commands.Context):
        """
        `a.fish` This command catches a fish. You then react with the emoji choice you want, either \"keep\" or \"sell\". If keep is chosen the fish will be added to your fish bucket if you have less than ten fish of the same rarity, otherwise it will be sold. If you choose sell the fish will be sold.
        """

        # Make sure they can't fish twice
        if ctx.author.id in self.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        self.current_fishers.append(ctx.author.id)

        # See what our chances of getting each fish are
        rarity = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]  # Chance of each rarity
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.94, .05, .01]
        )[0]  # Chance of modifier

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
        async with utils.DatabaseConnection() as db:
            user_inventory = await db("SELECT * FROM user_fish_inventory WHERE user_id=$1", ctx.author.id)
        for row in user_inventory:
            if row['fish'] == new_fish['raw_name']:
                amount = amount + 1
                
        owned_unowned = "Owned" if amount > 0 else "Unowned"
        print(new_fish["image"])
        # Tell the user about the fish they caught
        embed = discord.Embed()
        embed.title = f"You caught {a_an} {rarity} {new_fish['name']}!"
        embed.add_field(name=owned_unowned, value=f"You have {amount} {new_fish['name']}", inline=False)
        embed.set_image(url="attachment://new_fish.png")
        embed.color = utils.RARITY_CULERS[rarity]
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)

        # Ask if they want to sell the fish they just caught
        await self.ask_to_sell_fish(ctx.author, message, new_fish)

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

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx: commands.Context, old: str, new: str):
        """
        `a.rename "fish name"` Renames specified fish.
        """
        
        # Get the user's fish inventory based on the fish's name
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2;""", old, ctx.author.id)
            
        # Check if the user doesn't have the fish   
        if not fish_rows: 
            return await ctx.send(
                f"You have no fish named {old}!",
                allowed_mentions=discord.AllowedMentions.none()
            )
        
        # Update the database
        await db(
            """UPDATE user_fish_inventory SET fish_name=$1 WHERE user_id=$2 and fish_name=$3;""",
            new, ctx.author.id, old,
        )
        # Send confirmation message
        await ctx.send(
            f"Congratulations, you have renamed {old} to {new}!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def release(self, ctx: commands.Context, name: str):
        """
        `a.release "fish name"` Releases specified fish back into the wild.
        """

        # Get the user's fish inventory based on the fish's name
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT fish_name FROM user_fish_inventory WHERE fish_name=$1 and user_id=$2;""", name, ctx.author.id)
        
        # Check if the user has the fish
        if fish_rows:

            # Update the database
            async with utils.DatabaseConnection() as db:
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
