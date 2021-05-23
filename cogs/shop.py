# Badly made code for a shop, still WIP as it doesnt work lol
# import discord
# import utils
# import random
# import asyncio
# import typing
# from discord.ext import commands

# class Shop(commands.Cog):
#     def __init__(self, bot:commands.AutoShardedBot):
#         self.bot = bot

#     @commands.command(aliases=["s"])
#     @commands.bot_has_permissions(send_messages=True, embed_links=True)
#     async def shop(self, ctx:commands.Context):
#         embed = discord.Embed()
#         embed.title = "Fish Shop"
#         embed.add_field(name="Common Fish Bag", value=f"This gives you one fish with normal chances", inline=False)
#         embed.add_field(name="Uncommon Fish Bag", value=f"This gives you one fish with increased chances", inline=False)
#         embed.add_field(name="Rare Fish Bag", value=f"This gives you one fish with higher chances", inline=False)
#         embed.add_field(name="Epic Fish Bag", value=f"This gives you one fish with substantially better chances", inline=False)
#         embed.add_field(name="Legendary Fish Bag", value=f"This gives you one fish with extremely better chances", inline=False)
#         await ctx.send(embed=embed)

#     @commands.command(aliases=["b"])
#     @commands.bot_has_permissions(send_messages=True, embed_links=True)
#     async def buy(self, ctx:commands.Context, arg1:typing.Optional[str], arg2:typing.Optional[int]=1):
#         item = arg1
#         amount = arg2
#         if item == "Common Fish Bag":
#             async with utils.DatabaseConnection() as db:
#                 await db("""
#                     INSERT INTO user_item_inventory (user_id, cfs) VALUES ($1, $2);
#                     """, ctx.author.id, amount)

#     @commands.command(aliases=["u"])
#     @commands.bot_has_permissions(send_messages=True, embed_links=True)
#     async def use(self, ctx:commands.Context):
#         item = commands.Context
#         if item == "Common Fish Bag":
#             async with utils.DatabaseConnection() as db:
#                 await db("""
#                     UPDATE user_item_inventory SET cfb = cfb - 1 WHERE user_id = {ctx.author.id}""")
#             rarity = random.choices(
#             ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
#             [.6689, .2230, .0743, .0248, .0082, .0008,])[0]
        
#         new_fish = random.choice(list(self.bot.fish[rarity].values()))
        
#         embed = discord.Embed()
#         embed.title = f"You got a {rarity} {new_fish['name']}!"
#         embed.set_image(url="attachment://new_fish.png")
        
#         fish_file = discord.File(new_fish["image"], "new_fish.png")
#         message = await ctx.send(file=fish_file, embed=embed)
        
#         emojis = [844594478392147968, 844594468580491264]
#         gen = (x for x in self.bot.emojis if x.id in emojis)
#         for i in gen:
#             await message.add_reaction(i)
        
#         check = lambda reaction, user: reaction.emoji.id in emojis and user.id == ctx.author.id and reaction.message.id == message.id
#         try:
#             choice = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
#             choice = "sell" if choice[0].emoji.id == 844594478392147968 else "keep"
#         except asyncio.TimeoutError:
#             await ctx.send("Did you forget about me? I've been waiting for a while now! I'll just assume you wanted to sell the fish.")
#             choice = "sell"
        
#         if choice == "sell":
#             async with utils.DatabaseConnection() as db:
#                 await db("""
#                     INSERT INTO user_balance (user_id, balance) VALUES ($1, $2)
#                     ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + $2;
#                     """, ctx.author.id, new_fish["cost"])
#                 self.current_fishers.remove(ctx.author.id)
#             return await ctx.send(f"Sold your **{new_fish['name']}** for **{new_fish['cost']}**!")
        
#         await ctx.send("What do you want to name your new fish? (32 character limit)")
#         check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32
        
#         try:
#             name = await self.bot.wait_for("message", timeout=60.0, check=check)
#             name = name.content
#             return await ctx.send(f"You're new fish **{name}** has been added to your bucket!")
        
#         except asyncio.TimeoutError:
#             name = f"{random.choice(['Captain', 'Mr.', 'Mrs.', 'Commander'])} {random.choice(['Nemo', 'Bubbles', 'Jack', 'Finley', 'Coral'])}"
#             return await ctx.send(f"Did you forget about me? I've been waiting for a while now! I'll name the fish for you. Let's call it **{name}**")
        
#         finally:
#             async with utils.DatabaseConnection() as db:
#                 await db("""INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1, $2, $3)""", ctx.author.id, new_fish["raw_name"], name)
#             self.current_fishers.remove(ctx.author.id)
