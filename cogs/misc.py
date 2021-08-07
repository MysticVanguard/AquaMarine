import discord
from discord.ext import commands

from utils import config
import utils


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["latency"])
    @commands.bot_has_permissions(send_messages=True)
    async def ping(self, ctx:commands.Context):
        '''`a.ping` Checks the ping of the bot'''

        return await ctx.send(f'🏓 pong! Latency: `{round(self.bot.latency, 8)}ms`')

    @commands.command(aliases=["github"])
    @commands.bot_has_permissions(send_messages=True)
    async def git(self, ctx:commands.Context):
        '''`a.git` This command shows the github link for the bot.'''

        return await ctx.send(config["github"])

    @commands.command(aliases=["say"])
    @commands.bot_has_permissions(send_messages=True)
    async def echo(self, ctx:commands.Context, *, content:str):
        '''`a.echo` Repeats users message'''

        return await ctx.send(content)

    @commands.command(aliases=["status"])
    @commands.bot_has_permissions(send_messages=True)
    @commands.is_owner()
    async def activity(self, ctx:commands.Context, *, activity:str):
        '''`a.activity` Changes the status of the bot (owner command only)'''

        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        return await ctx.message.add_reaction('👌')

    @commands.command(aliases=["d"])
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    @commands.bot_has_permissions(send_messages=True)
    async def daily(self, ctx:commands.Context):
        """
        `a.daily` This command gives you a daily reward of **100** sand dollars.
        """

        # adds the money to the users bal
        async with utils.DatabaseConnection() as db:
            await db(
                """INSERT INTO user_balance (user_id, balance) VALUES ($1, 100)
                ON CONFLICT (user_id) DO UPDATE SET balance = user_balance.balance + 100""",
                ctx.author.id)

        # confirmation message
        return await ctx.send("Daily reward of 100 Sand Dollars <:sand_dollar:852057443503964201> claimed!")

    @daily.error
    async def daily_error(self, ctx, error):

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
        await ctx.send(f'Daily reward claimed, please try again in {round(time)} {form}.')
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def stab(self, ctx:commands.Context, user: discord.User = None):
        """
        `a.stab @user` This command has a fish stab a user.
        """
        if user.id == ctx.author.id:
            return await ctx.send("Your fish is too loyal to stab you!")
        await ctx.send(f"Your fish stabs {user.mention} with a knife, nice!", file=discord.File("C:/Users/JT/Pictures/Aqua/assets/images/background/stab.gif"))
def setup(bot):
    bot.add_cog(Misc(bot))
