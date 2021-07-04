import random
import typing
import re
import asyncio

import discord
from discord.ext import commands

import utils


HELP_TEXT = """
**For a list of commands, run `a.commands`!**\n Welcome to Aquamarine, your virtual fishing, fish care, and virtual aquarium bot! 
To start off run the `a.fish` command and react to one of the options. run the `a.firsttank` command to get your first tank for free, and start your adventure owning tanks. 
To deposit a fish into a tank use `a.dep "tank name" "fish name"` although remember, each tank has a limited capacity 
"""


class Help(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def help(self, ctx: commands.Context):
        await ctx.author.send(HELP_TEXT)









def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
