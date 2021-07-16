import random
import asyncio
import math
from datetime import datetime as dt, timedelta
import io
from PIL import Image
import imageio

import discord
from discord.ext import commands, tasks

import utils


class Upgrades(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        
    cost_to_upgrade_list = [125, 250, 500, 1000, 2000]

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrades(self, ctx:commands.Context):
        """
        `a.upgrades` This command shows you your upgrades and prices of them.
        """
        message =  []
        emote_string_list = []
        upgrade_description = {
            'line_upgrade': 'This upgrade makes your chance of getting two fish in one cast higher.', 
            'rod_upgrade': 'This upgrade makes the price a fish sells for when caught increase.', 
            'bait_upgrade': 'This upgrade makes it so your chances of catching higher rarity fish increase.', 
            'lure_upgrade': 'This upgrade increases the chance of getting  a golden or inverted fish.',
            'weight_upgrade': 'This upgrade increases the possible level a caught fish can be.'
            }
        async with utils.DatabaseConnection() as db:
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
            if not upgrades:
                await db("""INSERT INTO user_upgrades (user_id) VALUES ($1)""", ctx.author.id)
                upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
        for upgrade, level in upgrades[0].items():
            for i in range(level):
                emote_string_list.append("<:full_upgrade_bar:865028622766702602>")
            while len(emote_string_list) < 5:
                emote_string_list.append("<:empty_upgrade_bar:865028614561988649>")
            cost_string = f"Costs {self.cost_to_upgrade_list[int(level-1)]} to upgrade."
            if level == 5:
                emote_string_list = ["<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>"]
                cost_string = "This Upgrade is fully upgraded."
            message.append(f"<:left_upgrade_bar:865028588192661504>{''.join(emote_string_list)}<:right_upgrade_bar:865028605863919616> **{' '.join(upgrade.split('_')).title()}: Lvl. {level}. {cost_string}**\n*{upgrade_description[upgrade]}*")
            emote_string_list = []
        await ctx.send('\n'.join(message))
    
    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx:commands.Context, upgrade):
        """
        `a.upgrade "upgrade"` This command upgrades specified upgrade.
        """
        upgraded = f"{upgrade}_upgrade"
        async with utils.DatabaseConnection() as db:
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
        if upgraded not in upgrades[0].keys():
            return await ctx.send("That is not an upgrade.")
        for upgrade_iter in upgrades[0].keys():
            if upgraded == upgrade_iter:
                if upgrades[0][upgrade_iter] == 5:
                    return await ctx.send("That upgrade is fully upgraded.")
                if not await utils.check_price(ctx.author.id, self.cost_to_upgrade_list[upgrades[0][upgraded]]):
                    return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:852057443503964201> for this upgrade!")
        async with utils.DatabaseConnection() as db:
            await db("""UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", self.cost_to_upgrade_list[upgrades[0][upgraded]], ctx.author.id)
            await db("""UPDATE user_upgrades SET {0}=user_upgrades.{0}+1 WHERE user_id = $1""".format(upgraded), ctx.author.id)
        await ctx.send(f"{upgrade.title()} has been upgraded!")
        


def setup(bot):
    bot.add_cog(Upgrades(bot))