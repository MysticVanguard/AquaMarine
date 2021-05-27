import discord
import utils
import random
import asyncio
import typing
from discord.ext import commands


class Fishing(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        self.current_fishers = []
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context, user:typing.Optional[discord.Member]):
        '''Check's the user's or a member's balance'''
        async with utils.DatabaseConnection() as db:
            if user:
                fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", user.id)
                return await ctx.send(f"{user.display_name} has {fetched[0]['balance']} money!" if fetched else f"{user.display_name} has no money!")
            
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
            return await ctx.send(f"You have {fetched[0]['balance']} money!" if fetched else "You have no money!")
    
    
    @commands.command(aliases=["bucket"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fishbucket(self, ctx:commands.Context, target:typing.Optional[typing.Union[discord.Member, int]]=1, page_number:typing.Optional[int]=1):  
        '''Check's the user's or a member's fish bucket'''      
        if isinstance(target, discord.Member):
            user = target
            page = page_number
        elif isinstance(target, int):
            user = ctx.author
            page = target
        
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", user.id)
        if not fetched:
            return await ctx.send("You have no fish in your bucket!" if user == ctx.author else f"{user.display_name} has no fish in their bucket!")
        
        totalpages = len(fetched) // 5 + (len(fetched) % 5 > 0)
        if page < 1 or page > totalpages:
            return await ctx.send("That page is doesn't exist.")
        
        embed = discord.Embed()
        embed.title = f"{user.display_name}'s fish bucket"
        embed.set_footer(text=f"page {page}/{totalpages}")
        for i in fetched[page*5-5:page*5]:
            embed.add_field(name=i['fish_name'], value=f"This fish is a **{' '.join(i['fish'].split('_')).title()}**", inline=False)
        await ctx.send(embed=embed)
            
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fish(self, ctx:commands.Context):
        '''Fish's for a fish'''
        if ctx.author.id in self.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        
        self.current_fishers.append(ctx.author.id)
        
        rarity = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [.6689, .2230, .0743, .0248, .0082, .0008,])[0]
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.40, .50, .10])[0]
        new_fish = random.choice(list(self.bot.fish[rarity].values()))
        
        if special == "normal":
            pass
        elif special == "inverted":
            new_fish = utils.make_inverted(new_fish)
        elif special == "golden":
            new_fish = utils.make_golden(new_fish)
        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"
        print(new_fish)
        embed = discord.Embed()
        embed.title = f"You caught {a_an} {rarity} {new_fish['name']}!"
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
            await ctx.send("Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
            choice = "sell"
        
        if choice == "sell":
            async with utils.DatabaseConnection() as db:
                await db("""
                    INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2;
                    """, ctx.author.id, new_fish["cost"])
                self.current_fishers.remove(ctx.author.id)
            return await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
        
        await ctx.send("What do you want to name your new fish? (32 character limit)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32
        
        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"Your new fish **{name}** has been added to your bucket!")
        
        except asyncio.TimeoutError:
            name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
            return await ctx.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")
        
        finally:
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1, $2, $3)""", ctx.author.id, new_fish["raw_name"], name)
            self.current_fishers.remove(ctx.author.id)

    @fish.error
    async def fish_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'The fish are scared, please try again in {:.0f} seconds'.format(error.retry_after)
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
