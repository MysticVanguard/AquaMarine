import discord
import utils
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fish = bot.fish
        self.db = utils.DatabaseConnection
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
        
        if not fetched:
            return await ctx.send("You have no money!")
        await ctx.send(f"You have {feteched[0]['balance']} money!")
    
    
    @commands.command(aliases=["bucket"])
    @commands.bot_has_permissions(send_messages=True)
    async def fishbucket(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_fish_inventory WHERE user_id = $1""", ctx.author.id)
        
        if not fetched:
            return await ctx.send("You have no money!")
        await ctx.send(f"You have {feteched[0]['balance']} money!")

def setup(bot):
    bot.add_cog(MembersCog(bot))
