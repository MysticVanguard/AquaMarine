import discord
import utils
import random
import asyncio
import typing
import re
from discord.ext import commands

class tanks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def firsttank(self, ctx:commands.Context):
        async with utils.DatabaseConnection() as db:
            fetched = await db("""SELECT user_id FROM user_tank_inventory WHERE user_id=$1;""", ctx.author.id)
        if fetched:
            return await ctx.send(f"You have your first tank already!")
        else: 
            async with utils.DatabaseConnection() as db:
                await db("""INSERT INTO user_fish_inventory VALUES ($1, '{TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE}', '{"Fish Bowl"}');""", ctx.author.id)
        await ctx.send("What do you want to name your first tank? (32 character limit)")
        check = lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 32

        try:
            name = await self.bot.wait_for("message", timeout=60.0, check=check)
            name = name.content
            return await ctx.send(f"You have your new tank, **{name}**!")
        
        except asyncio.TimeoutError:
            name = "Starter Tank"
            return await ctx.send(f"Did you forget about me {ctx.author.mention}? I've been waiting for a while now! I'll name the tank for you. Let's call it **{name}**")
        
        finally:
            async with utils.DatabaseConnection() as db:
                await db("""UPDATE user_tank_inventory SET tank_1_name = '{$1}' WHERE user_id = $2;""", name, ctx.author.id)
def setup(bot):
    bot.add_cog(tanks(bot))