# Badly made code for a shop, still WIP as it doesnt work lol
import discord
import utils
import random
import asyncio
import typing
from discord.ext import commands

class Shop(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    @commands.command(aliases=["s"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shop(self, ctx:commands.Context):
        embed = discord.Embed()
        embed.title = "Fish Shop"
        embed.add_field(name="Fish Bags", value=f"These are bags containing a fish of a random rarity", inline=False)
        embed.add_field(name="Common Fish Bag", value=f"This gives you one fish with normal chances COST 100", inline=True)
        embed.add_field(name="Uncommon Fish Bag", value=f"This gives you one fish with increased chances COST 250", inline=True)
        embed.add_field(name="Rare Fish Bag", value=f"This gives you one fish with higher chances COST 450", inline=True)
        embed.add_field(name="Epic Fish Bag", value=f"This gives you one fish with substantially better chances COST 1000", inline=True)
        embed.add_field(name="Legendary Fish Bag", value=f"This gives you one fish with extremely better chances COST 1500", inline=True)
        embed.add_field(name="Mystery Fish Bag", value=f"This gives you one bag of a random rarity COST 500", inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=["b"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def buy(self, ctx:commands.Context, item:typing.Optional[str], amount:typing.Optional[int]=1):

        common_names = ["Common Fish Bag", "Common", "Cfb"]
        uncommon_names = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
        rare_names = ["Rare Fish Bag", "Rare", "Rfb"]
        epic_names = ["Epic Fish Bag", "Epic", "Efb"]
        legendary_names = ["Legendary Fish Bag", "Legendary", "Lfb"]
        mystery_names = ["Mystery Fish Bag", "Mystery", "Mfb"]
        all_names = [common_names, uncommon_names, rare_names, epic_names, legendary_names, mystery_names]
        
        if not any([item.title() in name_list for name_list in all_names]):
            return await ctx.send("That is not an available item")
           
        item_name_dict = {
            "cfb": (common_names, 100, "Common"),
            "ufb": (uncommon_names, 250, "Uncommon"),
            "rfb": (rare_names, 450, "Rare"),
            "efb": (epic_names, 1000, "Epic"),
            "lfb": (legendary_names, 1500, "Legendary"),
        }
        
        for table, data in item_name_dict.items():
            possible_entries = data[0]
            cost = data[1]
            rarity_response = data[2]
            
            if not check_price(ctx.author.id, cost):
                return await ctx.send("You don't have enough money for this!")
            
            if item.title() in possible_entries:
                async with utils.DatabaseConnection() as db:
                    await db("""
                    INSERT INTO user_item_inventory (user_id, $1) 
                    VALUES ($2, $3) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET $1=user_item_inventory.$1+excluded.$1""", table, ctx.author.id, amount)
        
        if item.title() in mystery_names:
            cost = 500
            rarity_type = random.choices(
                ["cfb", "ufb", "rfb", "efb", "lfb",],
                [.5, .3, .125, .05, .025,])[0]
            rarity_response = data[2]
            
            if not check_price(ctx.author.id, cost):
                return await ctx.send("You don't have enough money for this!")
                
            async with utils.DatabaseConnection() as db:
                await db("""
                        INSERT INTO user_item_inventory (user_id, $1) 
                        VALUES ($2, $3) 
                        ON CONFLICT (user_id) DO UPDATE 
                        SET $1=user_item_inventory.$1+excluded.$1""", rarity_type, ctx.author.id, amount)
        
        
        async with utils.DatabaseConnection() as db:
            await db("""
                UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", cost, ctx.author.id)
            
        await ctx.send(f"You Bought {amount} {rarity_response} Fish Bag for {amount * cost}!")
    
    # Returns true is a user_id has enough money based on the cost
    async def check_price(self, user_id, cost):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT balance FROM user_balance WHERE user_id = $1""", user_id)
            fetched = fetched[0]['balance']
        if fetched < cost:
            return False
        return True
    
    @commands.command(aliases=["u"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def use(self, ctx:commands.Context, used_item):
        common = .6689
        uncommon = .2230
        rare = .0743
        epic = .0248
        legendary = .0082
        mythic = .0008
       
        item = used_item
        print(item)
        fetched = ""
        
        if item.title() == "Common Fish Bag" or item.title() == "Common" or item.title() == "Cfb":
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT cfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                print(fetched)
                fetched = fetched[0]['cfb']
            if not fetched:
                return await ctx.send(f"You have no Common Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET cfb=cfb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Uncommon Fish Bag" or item.title() == "Uncommon" or item.title() == "Ufb":
            rarity = "ufb"
            rarity_response = "Uncommon"
            common = .6062
            uncommon = .2423
            rare = .0967
            epic = .0385
            legendary = .0154
            mythic = .0009
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT ufb FROM user_item_inventory WHERE user_id = $2""", ctx.author.id)
                print(fetched)
                fetched = fetched[0][rarity]
            if not fetched:
                return await ctx.send(f"You have no Uncommon Fish Bags!")
        if item.title() == "Rare Fish Bag" or item.title() == "Rare" or item.title() == "Rfb":
            rarity = "rfb"
            rarity_response = "Rare"
            common = .6689
            uncommon = .2230
            rare = .0743
            epic = .0248
            legendary = .0082
            mythic = .0008
        if item.title() == "Epic Fish Bag" or item.title() == "Epic" or item.title() == "Efb":
            rarity = "efb"
            rarity_response = "Epic"
            common = .5156
            uncommon = .2578
            rare = .1289
            epic = .0645
            legendary = .0322
            mythic = .0010
        if item.title() == "Legendary Fish Bag" or item.title() == "Legendary" or item.title() == "Lfb":
            rarity = "lfb"
            rarity_response = "Legendary"
            common = .4558
            uncommon = .2605
            rare = .1490
            epic = .0850
            legendary = .0486
            mythic = .0011



        rarity = random.choices(
        ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
        [common, uncommon, rare, epic, legendary, mythic,])[0]
        
        new_fish = random.choice(list(self.bot.fish[rarity].values()))
        
        embed = discord.Embed()
        embed.title = f"You got a {rarity} {new_fish['name']}!"
        embed.set_image(url="attachment://new_fish.png")
        
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
            return await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
        
        await ctx.send("What do you want to name your new fish? (32 character limit)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32
        
        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"You're new fish **{name}** has been added to your bucket!")
        
        except asyncio.TimeoutError:
            name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
            return await ctx.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")
        
        finally:
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1, $2, $3)""", ctx.author.id, new_fish["raw_name"], name)
    
def setup(bot):
    bot.add_cog(Shop(bot))
