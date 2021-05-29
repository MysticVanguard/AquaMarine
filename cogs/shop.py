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
        common_call = """
                    INSERT INTO user_item_inventory (user_id, cfb) 
                    VALUES ($1, $2) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET cfb=user_item_inventory.cfb+excluded.cfb
                    """
        uncommon_names = ["Uncommon Fish Bag", "Uncommon", "Ufb"]
        uncommon_call = """
                    INSERT INTO user_item_inventory (user_id, ufb) 
                    VALUES ($1, $2) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET ufb=user_item_inventory.ufb+excluded.ufb
                    """
        rare_names = ["Rare Fish Bag", "Rare", "Rfb"]
        rare_call = """
                    INSERT INTO user_item_inventory (user_id, rfb) 
                    VALUES ($1, $2) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET rfb=user_item_inventory.rfb+excluded.rfb
                    """
        epic_names = ["Epic Fish Bag", "Epic", "Efb"]
        epic_call = """
                    INSERT INTO user_item_inventory (user_id, efb) 
                    VALUES ($1, $2) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET efb=user_item_inventory.efb+excluded.efb
                    """
        legendary_names = ["Legendary Fish Bag", "Legendary", "Lfb"]
        legendary_call = """
                    INSERT INTO user_item_inventory (user_id, lfb) 
                    VALUES ($1, $2) 
                    ON CONFLICT (user_id) DO UPDATE 
                    SET lfb=user_item_inventory.lfb+excluded.lfb
                    """
        mystery_names = ["Mystery Fish Bag", "Mystery", "Mfb"]
        
        all_names = [common_names, uncommon_names, rare_names, epic_names, legendary_names, mystery_names]
        
        if not any([item.title() in name_list for name_list in all_names]):
            return await ctx.send("That is not an available item")
           
        item_name_dict = {
            "cfb": (common_names, 100, "Common", common_call),
            "ufb": (uncommon_names, 250, "Uncommon", uncommon_call),
            "rfb": (rare_names, 450, "Rare", rare_call),
            "efb": (epic_names, 1000, "Epic", epic_call),
            "lfb": (legendary_names, 1500, "Legendary", legendary_call)
        }
        
        for table, data in item_name_dict.items():
            
            possible_entries = data[0]
            
            if item.title() in possible_entries:
                    
                cost = data[1]
                rarity_response = data[2]
                db_call = data[3]
                
                if not await self.check_price(ctx.author.id, cost):
                    return await ctx.send("You don't have enough money for this!")
                
                async with utils.DatabaseConnection() as db:
                    await db(db_call, ctx.author.id, amount)
        
        if item.title() in mystery_names:
            cost = 500
            
            if not await self.check_price(ctx.author.id, cost):
                return await ctx.send("You don't have enough money for this!")
            
            rarity_type = random.choices(
                ["cfb", "ufb", "rfb", "efb", "lfb",],
                [.5, .3, .125, .05, .025,])[0]
            data = item_name_dict[rarity_type]
            rarity_response = data[2]
            db_call = data[3]
                
            async with utils.DatabaseConnection() as db:
                await db(db_call, ctx.author.id, amount)
        
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
        rarity_chances = {"cfb": {"common": .6689, "uncommon": .2230, "rare": .0743, "epic": .0248, "legendary": .0082, "mythic": .0008},
        "ufb": {"common": .6062, "uncommon": .2423, "rare": .0967, "epic": .0385, "legendary": .0154, "mythic": .0009},
        "rfb": {"common": .5156, "uncommon": .2578, "rare": .1289, "epic": .0645, "legendary": .0322, "mythic": .0010},
        "efb": {"common": .4558, "uncommon": .2605, "rare": .1490, "epic": .0850, "legendary": .0486, "mythic": .0011},
        "lfb": {"common": .3843, "uncommon": .2558, "rare": .1701, "epic": .1134, "legendary": .0752, "mythic": .0012}
        }
       
        item = used_item
        fetched = ""
        
        if item.title() == "Common Fish Bag" or item.title() == "Common" or item.title() == "Cfb":
            chances = rarity_chances["cfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT cfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['cfb']
            if not fetched:
                return await ctx.send(f"You have no Common Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET cfb=cfb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Uncommon Fish Bag" or item.title() == "Uncommon" or item.title() == "Ufb":
            chances = rarity_chances["ufb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT ufb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['ufb']
            if not fetched:
                return await ctx.send(f"You have no Uncommon Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET ufb=ufb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Rare Fish Bag" or item.title() == "Rare" or item.title() == "Rfb":
            chances = rarity_chances["rfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT rfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['rfb']
            if not fetched:
                return await ctx.send(f"You have no Rare Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET rfb=rfb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Epic Fish Bag" or item.title() == "Epic" or item.title() == "Efb":
            chances = rarity_chances["efb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT efb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['efb']
            if not fetched:
                return await ctx.send(f"You have no Epic Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET efb=efb-1 WHERE user_id = $1""", ctx.author.id)
        if item.title() == "Legendary Fish Bag" or item.title() == "Legendary" or item.title() == "Lfb":
            chances = rarity_chances["lfb"]
            async with utils.DatabaseConnection() as db:
                fetched = await db("""SELECT lfb FROM user_item_inventory WHERE user_id = $1""", ctx.author.id)
                fetched = fetched[0]['lfb']
            if not fetched:
                return await ctx.send(f"You have no Legendary Fish Bags!")
            async with utils.DatabaseConnection() as db:
                await db("""
                    UPDATE user_item_inventory SET lfb=lfb-1 WHERE user_id = $1""", ctx.author.id)


        print(chances)
        rarity = random.choices(
        ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
        [chances["common"], chances["uncommon"], chances["rare"], chances["epic"], chances["legendary"], chances["mythic"],])[0]
        special = random.choices(
            ["normal", "inverted", "golden",],
            [.94, .05, .01])[0]
        new_fish = random.choice(list(self.bot.fish[rarity].values()))
        
        if special == "normal":
            pass
        elif special == "inverted":
            new_fish = utils.make_inverted(new_fish)
        elif special == "golden":
            new_fish = utils.make_golden(new_fish)
        
        a_an = "an" if rarity[0].lower() in ("a", "e", "i", "o", "u") else "a"

        embed = discord.Embed()
        embed.title = f"You got {a_an} {rarity} {new_fish['name']}!"
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
            await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
            return utils.make_pure(new_fish, special)
        
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
            return utils.make_pure(new_fish, special)
    
def setup(bot):
    bot.add_cog(Shop(bot))
