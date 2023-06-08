import random
import asyncio
import discord
from datetime import datetime as dt, timedelta
from discord.ext import commands, tasks, vbu
import math

from cogs import utils
from cogs.utils import EMOJIS
from cogs.utils.fish_handler import FishSpecies


class Fishing(vbu.Cog):

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[

            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True)
    async def fish(self, ctx: commands.Context):
        """fish for a fish"""
        await utils.start_using(ctx, self.bot)
        await ctx.send("test")


def setup(bot):
    bot.add_cog(Fishing(bot))
    bot.fish = utils.fetch_fish("C:/Users/JT/Pictures/Aqua/assets/images/fish")
