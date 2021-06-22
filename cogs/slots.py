import random

import discord
from discord.ext import commands

import utils

# Dict of fish emojis
emoji_rarities = {
    "common": {
        "clownfish": "<:clownfish:849777027174760448>", "goldfish": "<:goldfish:849777027258515456>", "tiger_barb": "<:tiger_barb:849777027413311508>", "royal_blue_betta": "<:royal_blue_betta:849777027472031764>", "pufferfish": "<:pufferfish:849777027501522954>", 
        "oscar_cichlid": "<:oscar_cichlid:849777027599040522>", "neon_tetra_school": "<:neon_tetra_school:849777027326017586>", "turquoise_blue_betta": "<:turquoise_blue_betta:850970562469691433>", "tuna": "<:tuna:850970699359322122>", "squid": "<:squid:850970655695568906>",
        "shrimp": "<:shrimp:850970552830787624>", "red_betta": "<:red_betta:850970531216752660>", "paradise_fish": "<:paradise_fish:850970512695361546>", "koi": "<:koi:850970638599323678>", "headshield_slug": "<:headshield_slug:850970724231544833>",
        "guppies": "<:guppies:850970478884814908>", "electric_blue_hap": "<:electric_blue_hap:850970439136182293>", "cowfish": "<:cowfish:850970605276102658>", "clown_triggerfish": "<:clown_triggerfish:850970691628695562>", "angelfish": "<:angelfish:850970572569706526>",
        "pineapple_betta": "<:pineapple_betta:850970524414509056>", "harlequin_rasboras": "<:harlequin_rasboras:850970500686938112>", "electric_yellow_lab": "<:electric_yellow_lab:850970446648311828>", "catfish": "<:catfish:850970683718893578>",
        "blue_maomao": "<:blue_maomao:850970598784237568>", "blue_diamond_discus": "<:blue_diamond_discus:850970583499538464>", ":black_orchid_betta": "<:black_orchid_betta:850970430487527486>", "banggai_cardinalfish": "<:banggai_cardinalfish:850970420869070868>",
        "bottlenose_dolphin": "<:bottlenose_dolphin:850970711634739210>", "starfish": "<:starfish:850970666986766354>"
        },
    "uncommon": {
        "flowerhorn_cichlid": "<:flowerhorn_cichlid:849777027472293918>", "lionfish": "<:lionfish:849777027765633024>", "sea_bunny": "<:sea_bunny:850970830569209887>", "manta_ray": "<:manta_ray:850970787569860658>", "surge_wrasse": "<:surge_wrasse:850970772633550858>",
        "smalltooth_swordfish": "<:smalltooth_swordfish:850970859983470623>", "seal": "<:seal:850970851435479091>", "seahorse": "<:seahorse:850970763065688074>", "quoyi_parrotfish": "<:quoyi_parrotfish:850970754002845736>", "narwhal": "<:narwhal:850970796252069888>",
        "dumbo_octopus": "<:dumbo_octopus:850977726265163776>"
        },
    "rare": {
        "axolotl": "<:axolotl:850080397450149888>", "blobfish": "<:blobfish:850970966736764939>", "cuttlefish": "<:cuttlefish:850971019078664232>", "starfish_with_pants": "<:starfish_with_pants:850977707134025758>", "bobtail_squid": "<:bobtail_squid:850977717737619478>"
        },
    "epic": {
        "asian_arowana": "<:asian_arowana:850080397350010930>", "boesemani_rainbowfish": "<:boesemani_rainbowfish:850970734028914708>"
        },
    "legendary": {
        "anglerfish": "<:anglerfish:849777027769696297>"
        },
    "mythic": {
        "mandarinfish": "<:mandarinfish:850080397081182269>"
        }
}


class Slots(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def slots(self, ctx: commands.Context):
        """
        Rolls the slots
        """

        # See if the user has enough money
        if not await utils.check_price(ctx.author.id, 5):
            return await ctx.send("You don't have enough money for this! (5)")

        # Remove money from the user
        async with utils.DatabaseConnection() as db:
            await db("""UPDATE user_balance SET balance=balance-5 WHERE user_id = $1""", ctx.author.id)

        # Chooses the random fish for nonwinning rows
        chosen_fish = []
        rarities_of_fish = []
        for i in range(9):
            rarity_random = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]
            new_fish = random.choice(list(emoji_rarities[rarity_random]))
            rarities_of_fish.append(rarity_random)
            chosen_fish.append(new_fish)
        
        # Chooses winning fish
        rarity = random.choices(*utils.RARITY_PERCENTAGE_LIST)[0]
        fish_type = random.choice(list(emoji_rarities[rarity]))
        emoji_id = emoji_rarities[rarity][fish_type]

        # Find's the dict of winning fish
        fish_random_name = fish_type.replace("_", " ")
        used_fish = self.bot.fish[rarity][fish_random_name]

        # Checks if the user won
        win_or_lose = random.randint(1, 10)


        # Sends embed of either winning roll or losing roll
        embed = discord.Embed()
        embed.title = f"{ctx.author.display_name}'s roll..."
        row = []
        if win_or_lose == 2:
            for i in range(0, 6, 3):
                row.append(f"{emoji_rarities[rarities_of_fish[i]][chosen_fish[i]]}"
                f"{emoji_rarities[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                f"{emoji_rarities[rarities_of_fish[i+2]][chosen_fish[i+2]]}")
            row.append(f"{emoji_id}{emoji_id}{emoji_id}")
            embed.add_field(name="*spent 5 Sand Dollars <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Lucky", value=f"You won {fish_random_name.title()} :)", inline=False)
            message = await ctx.send(embed=embed)
            await self.bot.get_cog("Fishing").ask_to_sell_fish(ctx.author, message, used_fish)
        else:
            for i in range(0, 9, 3):
                row.append(f"{emoji_rarities[rarities_of_fish[i]][chosen_fish[i]]}"
                f"{emoji_rarities[rarities_of_fish[i+1]][chosen_fish[i+1]]}"
                f"{emoji_rarities[rarities_of_fish[i+2]][chosen_fish[i+2]]}")
            embed.add_field(name="*spent 5 Sand Dollars <:sand_dollar:852057443503964201>*", value="\n".join(row), inline=False)
            embed.add_field(name="Unlucky", value="You lost :(")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Slots(bot))
