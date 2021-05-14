import discord
import utils
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fish = bot.fish
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
        
        if not fetched:
            return await ctx.send("You have no money!")
        await ctx.send(f"You have {fetched[0]['balance']} money!")
    
    
    @commands.command(aliases=["bucket"])
    @commands.bot_has_permissions(send_messages=True)
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

def setup(bot):
    bot.add_cog(MembersCog(bot))
