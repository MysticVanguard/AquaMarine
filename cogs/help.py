import random
import typing
import re
import asyncio

import discord
from discord.ext import commands

import utils


HELP_TEXT_GENERAL = """
**For a list of commands, run `a.commands`!**\n Welcome to Aquamarine, your virtual fishing, fish care, and aquarium bot! 
To start off run the `a.fish` command and react to one of the options. run the `a.firsttank` command to get your first tank for free, and start your adventure owning tanks. 
To deposit a fish into a tank use `a.dep "tank name" "fish name"` (although remember, each tank has a limited capacity). Once a fish is
in a tank you can feed them (`a.feed "fish name"`) to keep them alive and entertain them (`a.entertain "fish name"`) to give them XP. 
To feed a fish, you need to buy fish food from the shop (`a.shop` to see the shop). To buy, use the `a.buy "item" "amount(optional)"` command.
To get help on certain commands, use `a.help "command"`.
"""


class Help(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    commands = {
        "bestiary": "`a.bestiary \"fish type (optional)\"` This command shows you a list of all the fish in the bot. If a fish is specified information about that fish is shown", 
        "fish": "`a.fish` This command catches a fish. You then react with the emoji choice you want, either \"keep\" or \"sell\". If keep is chosen the fish will be added to your fish bucket if you have less than ten fish of the same rarity, otherwise it will be sold. If you choose sell the fish will be sold.",
        "balance": "`a.balance \"user(optional)\"` This command checks your balance or another users.", 
        "fishbucket": "`a.fishbucket \"user(optional)\"` This command checks your fish bucket or another users. A user can only have ten max in each rarity in their fish bucket, but fish buckets don\'t include your deposited fish.", 
        "help": "`a.help \"command(optional)\"` This command shows a helpful paragraph and when a command is specified gives information about the command.", 
        "feed": "`a.feed \"fish name\"` This command feeds a fish in a tank with fish food, that can be bought. Fish food is needed to keep fish in tanks alive, and if a fish in a tank isnt feed once every five days, it dies.", 
        "entertain": "`a.entertain \"fish name\"` This command entertains a fish in a tank. Entertaining a fish gives the fish XP, which levels it up. The level of a fish determines how much money you earn when you clean its tank, and how much it can sell for.", 
        "clean": "`a.clean \"tank name\"` This command cleans a tank, which gives you sand dollars based on the level of the fish in the tank", 
        "git": "`a.git` This command shows the github link for the bot.", 
        "daily": "`a.daily` This command gives you a daily reward of **100** sand dollars.", 
        "shop": "`a.shop` This command shows everything buyable in the shop, along with their prices.", 
        "buy": "`a.buy \"item\" \"amount(optional)\"` This command buys an item from a shop, with the given value (default one, tanks and themes are always one).", 
        "use": "`a.use \"item\"` This command is only for using fish bags, using a fish bag is just like using the fish command.", 
        "slots": "`a.slots` This command roles the slots, which costs **5** sand dollars and can win you a fish.", 
        "deposit": "`a.deposit \"tank name\" \"fish name\"` This command deposits a specified fish into a specified tank.", 
        "show": "`a.show \"tank name\"` This command produces a gif of the specified tank.", 
        "firsttank": "`a.firsttank` This command gives you your first starter tank, a fish bowl. It needs to be done before you can buy tanks and themes."}
    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def help(self, ctx: commands.Context, command=typing.Optional[str]):
        if command not in commands.keys():
            await ctx.author.send(HELP_TEXT_GENERAL)
            return away ctx.send("Help DMed to you!")
        await ctx.author.send(commands[command])
        await ctx.send(f"Help for {command} DMed to you!")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    async def commands(self, ctx: commands.Context):
        embed = discord.Embed(title="Commands")
        embed.add_field(name="Keep in mind:", value="**anything in quotes is a variable, and the quotes may or may not be needed**", inline=True)
        for command_name, command in commands.items():
            embed.add_field(name=command_name, value=command, inline=False)
        await ctx.send(embed=embed)







def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
