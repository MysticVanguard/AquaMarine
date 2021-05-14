import discord
import utils
import random
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fish = bot.fish
        self.current_fishers = []
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
        
        if not fetched:
            return await ctx.send("You have no money!")
        await ctx.send(f"You have {fetched[0]['balance']} money!")
    
    
    @commands.command(aliases=["bucket"])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fishbucket(self, ctx:commands.Context, user:discord.Member = None):
        user = user or ctx.author
        
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", user.id)
        
        if not fetched:
            if user == ctx.author:
                return await ctx.send("You have no fish in your bucket!")
            return await ctx.send(f"{user.display_name} has no fish in their bucket!")
        
        embed = discord.Embed()
        embed.title = f"{user.display_name}\'s fish bucket"
        
        for i in fetched:
            embed.add_field(name=i['fish_name'], value=f"This fish is a **{i['fish']}**", inline=False)
            
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, attachments=True)
    async def fish(self, ctx:commands.Context):
        if ctx.author.id in self.current_fishers:
            return await ctx.send(f"{ctx.author.display_name}, you're already fishing!")
        
        self.current_fishers.append(ctx.author.id)
        
        rarity = random.choices(
            ["common", "uncommon", "rare", "epic", "legendary", "mythic",],
            [.6689, .2230, .0743, .0248, .0082, .0008,])
        
        new_fish = random.choice(self.fish[rarity])
        
        embed = discord.Embed()
        embed.title = f"You caught a {rarity} {new_fish['name']}!"
        embed.set_image(url="attachment://new_fish.png")
        fish_file = discord.File(new_fish["image"], )
        
        await ctx.send(file=fish_file, embed=embed)
        

def setup(bot):
    bot.add_cog(MembersCog(bot))
