import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.command(aliases=["latency"])
    @commands.bot_has_permissions(send_messages=True)
    async def ping(self, ctx:commands.Context):
        return await ctx.send(f'🏓 pong! Latency: `{round(self.bot.latency, 8)}ms`')
    
    @commands.command(aliases=["github"])
    @commands.bot_has_permissions(send_messages=True)
    async def git(self, ctx:commands.Context):
        return await ctx.send('https://github.com/MysticVanguard/AquaMarine')
    
    @commands.command(aliases=["say"])
    @commands.bot_has_permissions(send_messages=True)
    async def echo(self, ctx:commands.Context, *, content:str):
        return await ctx.send(content)
    
    @commands.command(aliases=["status"])
    @commands.bot_has_permissions(send_messages=True)
    @commands.is_owner()
    async def activity(self, ctx:commands.Context, *, activity:str):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        return await ctx.message.add_reaction('👌')

def setup(bot):
    bot.add_cog(Misc(bot))
