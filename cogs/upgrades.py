"""Manage upgrade tree and allow user to upgrade items"""
from typing import NamedTuple

from discord.ext import commands, vbu

from cogs import utils
from cogs.utils import EMOJIS


tier_ranks = {
    "rod_upgrade": {
        "bait_upgrade": {
            "line_upgrade": None,
            "lure_upgrade": None,
        },
        "crate_chance_upgrade": {
            "weight_upgrade": None,
            "crate_tier_upgrade": None,
        },
    },
    "bleach_upgrade": {
        "toys_upgrade": {
            "amazement_upgrade": None,
            "mutation_upgrade": None,
        },
        "big_servings_upgrade": {
            "hygienic_upgrade": None,
            "feeding_upgrade": None,
        },
    },
}


def get_tier(tier: int) -> dict:
    """Return a combined dictionary from a given tier"""
    if tier == 1:
        return tier_ranks
    sub_tier: dict = {}
    for val in get_tier(tier - 1).values():
        sub_tier |= val
    return sub_tier


class UpgradeTiers:
    """Functions to get info about the upgrade tree"""

    def __init__(self):
        self.tier_1 = get_tier(1)
        self.tier_2 = get_tier(2)
        self.tier_3 = get_tier(3)

    def get_parent(self, upgrade: str) -> str:
        """Return the parent node of an upgrade"""
        if upgrade in self.tier_1:
            return upgrade
        if upgrade in self.tier_2:
            tier = self.tier_1
        elif upgrade in self.tier_3:
            tier = self.tier_2
        return [key for key, val in tier.items() if upgrade in val][0]

    def last_upgrade_in_tier(self, upgrade: str) -> bool:
        """Return whether an upgrade is the last child"""
        if upgrade in self.tier_1:
            return upgrade == list(self.tier_1)[-1]
        if upgrade in self.tier_2:
            tier = self.tier_1
        elif upgrade in self.tier_3:
            tier = self.tier_2
        return upgrade in [list(v)[-1] for k, v in tier.items()]

    def flatten_tree(self, tier: dict, ret: list = None) -> list:
        """Traverse a nested dict"""
        if ret is None:
            ret = []
        for key, val in tier.items():
            ret.append(key)
            if val:
                self.flatten_tree(val, ret)
        return ret


class UpgradeInfo(NamedTuple):
    """Simple class to store upgrade info"""

    description: str
    name: str
    cost_string: str


class Pipes(NamedTuple):
    """Simple class to store emojis"""

    downspouts: str
    branches: str
    connection: str
    progess_bar: str


tiers = UpgradeTiers()


class Upgrades(vbu.Cog):
    """Commands to display upgrade tree and upgrade items"""

    UPGRADE_DESCRIPTIONS = dict(
        rod_upgrade="Increases the price a caught fish sells for",
        line_upgrade="Increases the chance of catching two fish in one cast",
        crate_chance_upgrade="Increases chance of catching a crate when fishing",
        weight_upgrade="Increases the level fish are when caught",
        bait_upgrade="Increases the chance of catching rarer fish when fishing",
        crate_tier_upgrade="Increases the tier of the crate caught",
        lure_upgrade="Increases the chance of catching a special fish when fishing",
        feeding_upgrade="Increases how long fish will live after being fed",
        toys_upgrade="Increases the xp gained from entertaining",
        mutation_upgrade="Increases the chance of a fish mutating \
            to a special fish during cleaning",
        amazement_upgrade="Increases chance of bonus level when entertaining",
        bleach_upgrade="Increases the cleaning multiplier",
        big_servings_upgrade="Increases chance of a fish not eating food when they are fed",
        hygienic_upgrade="Lessens the frequency of cleaning, while \
            giving a multiplier equal to the lost time",
    )

    UPGRADE_COST_TIER_1 = (1000, 2000, 3000, 4000, 5000, 5000)
    UPGRADE_COST_TIER_2 = (10000, 20000, 30000, 40000, 50000, 50000)
    UPGRADE_COST_TIER_3 = (100000, 200000, 300000, 400000, 500000, 500000)
    MAX_LEVEL = 5

    def get_cost_list(self, upgrade: str) -> tuple:
        """Return which cost list to use based on upgrade"""
        if upgrade in tiers.tier_1:
            return self.UPGRADE_COST_TIER_1
        if upgrade in tiers.tier_2:
            return self.UPGRADE_COST_TIER_2
        if upgrade in tiers.tier_3:
            return self.UPGRADE_COST_TIER_3
        return ()

    def parent_needs_upgraded(self, upgrades: dict, upgrade: str) -> bool:
        """Checks if parent upgrade still needs upgraded"""
        if upgrade in tiers.tier_2 | tiers.tier_3:
            parent = tiers.get_parent(upgrade)
            if upgrades[parent] != self.MAX_LEVEL:
                return True
        return False

    def get_upgrade_info(
        self, upgrades: dict, upgrade: str, level: int
    ) -> UpgradeInfo:
        """Return the details of a given upgrade"""
        cost_list = self.get_cost_list(upgrade)
        if self.parent_needs_upgraded(upgrades, upgrade):
            description = "???"
            name = "???"
            cost_string = "???"
        else:
            description = self.UPGRADE_DESCRIPTIONS[upgrade]
            name = " ".join(upgrade.split("_")).title()
            if level == self.MAX_LEVEL:
                cost_string = "This Upgrade is fully upgraded."
            else:
                cost_string = (
                    f"{cost_list[int(level)]:,} {EMOJIS['sand_dollar']}"
                )
        return UpgradeInfo(description, name, cost_string)

    @staticmethod
    def get_emoji_pieces(upgrade: str) -> Pipes:
        """Gather up emoji pipes needed for the upgrade tree"""
        if upgrade in tiers.tier_1:
            downspouts = ""
            branches = ""
            connection = EMOJIS["bar_L"]
            progess_bar = EMOJIS["bar_1"]
        elif upgrade in tiers.tier_2:
            downspouts = EMOJIS["straight"]
            if not tiers.last_upgrade_in_tier(upgrade):
                branches = EMOJIS["straight_branch"]
            else:
                branches = EMOJIS["branch"]
            connection = EMOJIS["bar_L_branch"]
            progess_bar = EMOJIS["bar_2"]
        elif upgrade in tiers.tier_3:
            if not tiers.last_upgrade_in_tier(tiers.get_parent(upgrade)):
                prepend = EMOJIS["straight"]
            else:
                prepend = EMOJIS["bar_empty"]
            downspouts = prepend + EMOJIS["straight"]
            if not tiers.last_upgrade_in_tier(upgrade):
                branches = prepend + EMOJIS["straight_branch"]
            else:
                branches = prepend + EMOJIS["branch"]
            connection = EMOJIS["bar_L_straight"]
            progess_bar = EMOJIS["bar_3"]
        return Pipes(downspouts, branches, connection, progess_bar)

    def create_message_block(
        self, level: int, info: UpgradeInfo, pipes: Pipes
    ) -> tuple:
        """Put upgrade descriptions and tree pieces together in a message"""
        completed_levels = pipes.progess_bar * level
        pending_levels = EMOJIS["bar_e"] * (self.MAX_LEVEL - level)

        progess_bar_bar = (
            f"{completed_levels}{pending_levels}{EMOJIS['bar_R']}"
        )
        new_line = "\n"
        message = (
            f"{pipes.downspouts}**{info.name}: "
            f"(Lvl. {level}.): {info.cost_string}**"
            f"{new_line}{pipes.downspouts}*{info.description}*",
            f"{pipes.branches}{pipes.connection}{progess_bar_bar}",
        )
        return message

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrades(self, ctx: commands.Context):
        """Show you your upgrades and the price of the next level."""

        # Grab their upgrades from the database
        async with vbu.Database() as db:
            upgrades = await db(
                f"""SELECT {", ".join(tiers.flatten_tree(tiers.tier_1))}
                FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )
            if not upgrades:
                upgrades = await db(
                    """INSERT INTO user_upgrades (user_id)
                    VALUES ($1) RETURNING *""",
                    ctx.author.id,
                )
        upgrades = upgrades[0]

        # Build message
        message = []
        for upgrade, level in upgrades.items():
            if upgrade == "user_id":
                continue
            info = self.get_upgrade_info(upgrades, upgrade, level)
            pipes = self.get_emoji_pieces(upgrade)
            if upgrade in tiers.tier_1:
                if list(tiers.tier_1).index(upgrade) == 0:
                    message.append(
                        (
                            "The Way of the Fish",
                            "These upgrades have to do with fishing",
                        )
                    )
                elif list(tiers.tier_1).index(upgrade) == 1:
                    message.append(("** **", "** **"))
                    message.append(
                        (
                            "The Way of the Tank",
                            "These upgrades have to do with owning fish in aquariums",
                        )
                    )
            message.append(self.create_message_block(level, info, pipes))
        message.append(("** **", "** **"))

        # And send our message
        embed = vbu.Embed()
        for name, value in message:
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def upgrade(self, ctx: commands.Context, *, upgrade: str):
        """Upgrade one of your items"""

        # Grab the user's current upgrades
        async with vbu.Database() as db:
            upgrades = await db(
                f"""SELECT {", ".join(tiers.flatten_tree(tiers.tier_1))}
                FROM user_upgrades WHERE user_id = $1""",
                ctx.author.id,
            )

        upgrades = upgrades[0]
        upgrade_base_name = upgrade.lower().removesuffix(" upgrade")
        upgrade = upgrade_base_name.replace(" ", "_") + "_upgrade"
        cost_list = self.get_cost_list(upgrade)

        if not cost_list:
            return await ctx.send("That's not a valid upgrade.")

        def upgrade_error(parent_upgrade: str) -> str:
            parent_upgrade = parent_upgrade.replace("_", " ").title()
            error_msg = f"The {parent_upgrade} needs upgraded first!"
            return error_msg

        if self.parent_needs_upgraded(upgrades, upgrade):
            parent = tiers.get_parent(upgrade)
            return await ctx.send(upgrade_error(parent))

        upgrade_level = upgrades[upgrade]
        if upgrade_level == self.MAX_LEVEL:
            return await ctx.send("That upgrade is fully upgraded.")

        if not await utils.check_price(
            self.bot,
            ctx.author.id,
            cost_list[int(upgrade_level)],
            "balance",
        ):
            return await ctx.send(
                f"You don't have enough Sand Dollars {EMOJIS['sand_dollar']} for this upgrade!"
            )

        # Upgrade them in the database
        async with vbu.Database() as db:
            await db(
                """UPDATE user_balance SET balance=balance-$1 WHERE user_id = $2""",
                cost_list[int(upgrades[upgrade])],
                ctx.author.id,
            )
            await db(
                f"""UPDATE user_upgrades SET {upgrade}=user_upgrades.{upgrade}+1
                WHERE user_id = $1""",
                ctx.author.id,
            )

        # And bam
        await ctx.send(
            f"You bought the Level {upgrade_level + 1} "
            f"{upgrade_base_name.title()} Upgrade for "
            f"{cost_list[upgrade_level]:,}!"
        )


def setup(bot):
    """Bot Setup"""
    bot.add_cog(Upgrades(bot))
