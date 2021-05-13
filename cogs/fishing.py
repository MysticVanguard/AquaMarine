import discord
import utils
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(aliases=["bal"])
    @commands.bot_has_permissions(send_messages=True)
    async def balance(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT * FROM user_balance WHERE user_id = $1""", ctx.author.id)
        
        if fetched:
            await ctx.send(f"You have {feteched[0]['balance']} money!")
        else:
            await ctx.send("You have no money!")

def setup(bot):
    bot.add_cog(MembersCog(bot))
