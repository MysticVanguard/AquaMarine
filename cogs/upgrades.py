import voxelbotutils as vbu
from discord.ext import commands
from cogs import utils

class Upgrades(vbu.Cog):

    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot
        self.UPGRADE_COST_LIST = [125, 250, 500, 1000, 2000]

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrades(self, ctx:commands.Context):
        """
        This command shows you your upgrades and prices of them.
        """

        message =  []
        emote_string_list = []
        upgrade_description = {
            'line_upgrade': 'This upgrade makes your chance of getting two fish in one cast higher.',
            'rod_upgrade': 'This upgrade makes the price a fish sells for when caught increase.',
            'bait_upgrade': 'This upgrade makes it so your chances of catching higher rarity fish increase.',
            'lure_upgrade': 'This upgrade increases the chance of getting an inverted or golden fish.',
            'weight_upgrade': 'This upgrade increases the possible level a caught fish can be.'
            }
        async with self.bot.database() as db:
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
            if not upgrades:
                await db("""INSERT INTO user_upgrades (user_id) VALUES ($1)""", ctx.author.id)
                upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
        for upgrade, level in upgrades[0].items():
            for _ in range(level):
                emote_string_list.append("<:full_upgrade_bar:865028622766702602>")
            while len(emote_string_list) < 5:
                emote_string_list.append("<:empty_upgrade_bar:865028614561988649>")
            cost_string = f"Costs {self.UPGRADE_COST_LIST[int(level-1)]} to upgrade."
            if level == 5:
                emote_string_list = ["<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>", "<:full_upgrade_bar:865028622766702602>"]
                cost_string = "This Upgrade is fully upgraded."
            message.append(f"<:left_upgrade_bar:865028588192661504>{''.join(emote_string_list)}<:right_upgrade_bar:865028605863919616> **{' '.join(upgrade.split('_')).title()}: Lvl. {level}. {cost_string}**\n*{upgrade_description[upgrade]}*")
            emote_string_list = []
        await ctx.send('\n'.join(message))

    @vbu.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx:commands.Context, upgrade):
        """
        This command upgrades specified upgrade.
        """

        upgraded = f"{upgrade}_upgrade"
        async with self.bot.database() as db:
            upgrades = await db("""SELECT rod_upgrade, bait_upgrade, weight_upgrade, line_upgrade, lure_upgrade FROM user_upgrades WHERE user_id = $1""", ctx.author.id)
        if upgraded not in upgrades[0].keys():
            return await ctx.send("That is not an upgrade.")
        for upgrade_iter in upgrades[0].keys():
            if upgraded == upgrade_iter:
                if upgrades[0][upgrade_iter] == 5:
                    return await ctx.send("That upgrade is fully upgraded.")
                if not await utils.check_price(self.bot, ctx.author.id, self.UPGRADE_COST_LIST[upgrades[0][upgraded]]):
                    return await ctx.send("You don't have enough Sand Dollars <:sand_dollar:852057443503964201> for this upgrade!")
        async with self.bot.database() as db:
            await db("""UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""", self.UPGRADE_COST_LIST[upgrades[0][upgraded]], ctx.author.id)
            await db("""UPDATE user_upgrades SET {0}=user_upgrades.{0}+1 WHERE user_id = $1""".format(upgraded), ctx.author.id)
        await ctx.send(f"{upgrade.title()} has been upgraded!")



def setup(bot):
    bot.add_cog(Upgrades(bot))