import discord
import utils
import random
import asyncio
import typing
import re
from discord.ext import commands


class Fishing(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        self.current_fishers = []
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context, user:typing.Optional[discord.Member]):
        '''Checks the users or a member's balance'''
        async with utils.DatabaseConnection() as db:
            if user:
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user.id)
                return await ctx.send(f"{user.display_name} has {fetched[0]['balance']} money!" if fetched else f"{user.display_name} has no money!")
            
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            return await ctx.send(f"You have {fetched[0]['balance']} money!" if fetched else "You have no money!")
    
    
    @commands.command(aliases=["bucket"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fishbucket(self, ctx:commands.Context, user:discord.User=None):  
        '''Shows a user's fish bucket'''   

        # Default the user to the author of the command
        user = user or ctx.author
        
        async with utils.DatabaseConnection() as db:
            fish_rows = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", user.id)
            
        if not fish_rows:
            return await ctx.send("You have no fish in your bucket!" if user == ctx.author else f"{user.display_name} has no fish in their bucket!")

        # totalpages = len(fetched) // 5 + (len(fetched) % 5 > 0)
        # if page < 1 or page > totalpages:
        #     return await ctx.send("That page is doesn't exist.")
        
        embed = discord.Embed()
        embed.title = f"{user.display_name}'s Fish Bucket"
        # embed.set_footer(text=f"page {page}/{totalpages}")

        fish_list = [(i['fish_name'], i['fish']) for i in fish_rows] # List of tuples (Fish Name, Fish Type)
        fish_list = sorted(fish_list, key=lambda x: x[1])

        fields = [] # The "pages" that the user can scroll through are the different rarity levels

        sorted_fish = {
            "common": [],
            "uncommon": [],
            "rare": [],
            "epic": [],
            "legendary": [],
            "mythic": []
        }
        
        # Sorted Fish will become a dictionary of {rarity: [list of fish names of fish in that category]} if the fish is in the user's inventory
        for rarity, fish_types in self.bot.fish.items(): # For each rarity level
            for _, fish_detail in fish_types.items(): # For each fish in that level
                raw_name = fish_detail["raw_name"]
                for user_fish_name, user_fish in fish_list:
                    if raw_name == self.get_normal_name(user_fish): # If the fish in the user's list matches the name of a fish in the rarity catgeory
                        sorted_fish[rarity].append((user_fish_name, user_fish)) # Append to the dictionary


        # Get the display string for each field
        for rarity, fish_list in sorted_fish.items():
            if fish_list:
                fish_string = [f"\"{fish_name}\": **{' '.join(fish_type.split('_')).title()}**" for fish_name, fish_type in fish_list]
                fields.append((rarity.title(), "\n".join(fish_string)))

        # Create an embed
        curr_index = 1
        curr_field = fields[curr_index-1]
        embed = self.create_fish_embed(user, curr_field)

        fish_message = await ctx.send(embed=embed) 

        valid_reactions = ["◀️", "▶️", "⏹️", "🔢"]
        [await fish_message.add_reaction(reaction) for reaction in valid_reactions] # Add the pagination reactions to the message

        def reaction_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in valid_reactions and reaction.message == fish_message
        
        while True: # Keep paginating until the user clicks stop
            try:
                chosen_reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                chosen_reaction = chosen_reaction.emoji
            except asyncio.TimeoutError:
                chosen_reaction = "⏹️"

            if chosen_reaction == "◀️":
                curr_index = max(1, curr_index - 1) # Keep the index in bounds
                curr_field = fields[curr_index-1]

                await fish_message.edit(embed=self.create_fish_embed(user, curr_field))

            elif chosen_reaction == "▶️":
                curr_index = min(len(fields), curr_index + 1) # Keep the index in bounds
                curr_field = fields[curr_index-1]

                await fish_message.edit(embed=self.create_fish_embed(user, curr_field))

            elif chosen_reaction == "⏹️":
                [await fish_message.remove_reaction(reaction, ctx.guild.me) for reaction in valid_reactions] # Remove the pagination emojis
                break # End the while loop

            elif chosen_reaction == "🔢":
                number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")
                # Check for custom message
                def message_check(message):
                    return message.author == ctx.author and message.channel == fish_message.channel and message.content.isdigit()

                user_message = await self.bot.wait_for('message', check=message_check)
                user_input = int(user_message.content)

                curr_index = min(len(fields), max(1, user_input))
                curr_field = fields[curr_index-1]

                await fish_message.edit(embed=self.create_fish_embed(user, curr_field))
                await number_message.delete()

                try:
                    await user_message.delete()
                except Exception:
                    pass


    def create_fish_embed(self, user, field):
        embed = discord.Embed() # Create a new embed to edit the message
        embed.title = f"**{user.display_name}'s Fish Bucket**\n"
        embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)

        return embed

    def get_normal_name(self, fish_name):
        match = re.match(r"(inverted_|golden_)(?P<fish_name>.*)", fish_name)
        if match:
            return match.group("fish_name")
        else:
            return fish_name

    @commands.command()
    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx:commands.Context):
        '''Fishes for a fish'''
        if ctx.author.id in self.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        
        self.current_fishers.append(ctx.author.id)
        
        rarity = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [.6689, .2230, .0743, .0248, .0082, .0008,])[0]
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.94, .05, .01])[0]
        new_fish = random.choice(list(self.bot.fish[rarity].values()))
        amount = 0
        owned_unowned = "Owned"
        if special == "normal":
            pass
        elif special == "inverted":
            new_fish = utils.make_inverted(new_fish)
        elif special == "golden":
            new_fish = utils.make_golden(new_fish)
        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
        for i in fetched:
            if i[1] == new_fish['raw_name']:
                amount = amount + 1
        if amount == 0:
            owned_unowned = "Unowned"
        embed = discord.Embed()
        embed.title = f"You caught {a_an} {rarity} {new_fish['name']}!"
        embed.add_field(name=owned_unowned, value=f"You have {amount} {new_fish['name']}", inline=False)
        embed.set_image(url="attachment://new_fish.png")
        # Choose a color
        embed.color = {
            # 0xHexCode
            "common": 0xFFFFFE, # White - FFFFFF doesn't work with Discord
            "uncommon": 0x75FE66, # Green
            "rare": 0x4AFBEF, # Blue
            "epic": 0xE379FF, # Light Purple
            "legendary": 0xFFE80D, # Gold
            "mythic": 0xFF0090 # Hot Pink
        }[rarity]
        
        
        fish_file = discord.File(new_fish["image"], "new_fish.png")
        message = await ctx.send(file=fish_file, embed=embed)
        
        emojis = [844594478392147968, 844594468580491264]
        gen = (x for x in self.bot.emojis if x.id in emojis)
        for i in gen:
            await message.add_reaction(i)
        
        check = lambda reaction, user: reaction.emoji.id in emojis and user.id == ctx.author.id and reaction.message.id == message.id
        try:
            choice = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            choice = "sell" if choice[0].emoji.id == 844594478392147968 else "keep"
        except asyncio.TimeoutError:
            await ctx.send(f"Did you forget about me {ctx.author.mention}? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
            choice = "sell"
        
        if choice == "sell":
            async with utils.DatabaseConnection() as db:
                await db("""
                    INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2;
                    """, ctx.author.id, new_fish["cost"])
            self.current_fishers.remove(ctx.author.id)
            await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
            return utils.make_pure(new_fish, special)
        
        fish_names = []
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
        for i in fetched:
            fish_names.append(i[2])
        print(fish_names)

        await ctx.send("What do you want to name your new fish? (32 character limit and cannot be named the same as another fish you own)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32 and m.content not in fish_names
        
        
        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"Your new fish **{name}** has been added to your bucket!")
        
        except asyncio.TimeoutError:
            name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
            return await ctx.send(f"Did you forget about me {ctx.author.mention}? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")
        
        finally:
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1, $2, $3)""", ctx.author.id, new_fish["raw_name"], name)
            self.current_fishers.remove(ctx.author.id)
            utils.make_pure(new_fish, special)

    @fish.error
    async def fish_error(self, ctx, error):
        time = error.retry_after
        form = 'seconds'
        if error.retry_after < 1.5:
            form = 'second'
        if error.retry_after > 3600:
            time = error.retry_after / 3600
            form = 'hours'
            if error.retry_after < 5400:
                form = 'hour'
        elif error.retry_after > 60:
            time = error.retry_after / 60
            form = 'minutes'
            if error.retry_after < 90:
                form = 'minute'
        if isinstance(error, commands.CommandOnCooldown):
            msg = f'The fish are scared, please try again in {round(time)} {form}.'
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def rename(self, ctx:commands.Context, old, new):
        '''Rename's your fish'''
        async with utils.DatabaseConnection() as db:
            await db("""UPDATE user_fish_inventory SET fish_name = $1 WHERE user_id = $2 and fish_name = $3""", new, ctx.author.id, old)
        await ctx.send(f"Congratulations, you have renamed {old} to {new}!")
    
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def release(self, ctx:commands.Context, name):
        '''Releases fish back into the wild'''
        async with utils.DatabaseConnection() as db:
            await db("""DELETE FROM user_fish_inventory WHERE fish_name = $1 and user_id = $2""", name, ctx.author.id)
        await ctx.send(f"Goodbye {name}!")

def setup(bot):
    bot.add_cog(Fishing(bot))
