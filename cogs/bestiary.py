import discord
from discord.ext import commands
import asyncio
import typing

class Bestiary(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bestiary(self, ctx:commands.Context, fish_name: typing.Optional[str]):
        '''Gets info on fish specified or all fish if none specified'''
        new_fish = {}
        fields = []
        if not fish_name:
            embed = discord.Embed()
            embed.title = "All Fish"
            for rarity, fish_types in self.bot.fish.items():
                fish_string = [f"**{' '.join(fish_type.split('_')).title()}**" for fish_type, fish_info in fish_types.items()]
                fields.append((rarity.title(), "\n".join(fish_string)))

            # Create an embed
            curr_index = 1
            curr_field = fields[curr_index - 1]
            embed = self.create_bucket_embed(ctx.author, curr_field)

            fish_message = await ctx.send(embed=embed)

            valid_reactions = ["◀️", "▶️", "⏹️", "🔢"]
            [await fish_message.add_reaction(reaction) for reaction in valid_reactions]  # Add the pagination reactions to the message

            def reaction_check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in valid_reactions and reaction.message == fish_message

            while True:  # Keep paginating until the user clicks stop
                try:
                    chosen_reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                    chosen_reaction = chosen_reaction.emoji
                except asyncio.TimeoutError:
                    chosen_reaction = "⏹️"
                
                index_chooser = {
                    "◀️": max(1, curr_index - 1),
                    "▶️": min(len(fields), curr_index + 1)
                }
                
                if chosen_reaction in index_chooser.keys():
                    curr_index = index_chooser[chosen_reaction]  # Keep the index in bounds
                    curr_field = fields[curr_index - 1]

                    await fish_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field))

                elif chosen_reaction == "⏹️":
                    await fish_message.clear_reactions()
                    break  # End the while loop

                elif chosen_reaction == "🔢":
                    number_message = await ctx.send(f"What page would you like to go to? (1-{len(fields)}) ")

                    # Check for custom message
                    def message_check(message):
                        return message.author == ctx.author and message.channel == fish_message.channel and message.content.isdigit()

                    user_message = await self.bot.wait_for('message', check=message_check)
                    user_input = int(user_message.content)

                    curr_index = min(len(fields), max(1, user_input))
                    curr_field = fields[curr_index - 1]

                    await fish_message.edit(embed=self.create_bucket_embed(ctx.author, curr_field))
                    await number_message.delete()
                    await user_message.delete()

                    
        else:
            for rarity, fish_types in self.bot.fish.items():
                for fish_type, fish_info in fish_types.items():
                    if fish_info["name"] == str(fish_name.title()):
                        new_fish = fish_info
            embed = discord.Embed()
            embed.title = new_fish['name']
            embed.set_image(url="attachment://new_fish.png")
            embed.add_field(name='Rarity', value=f"This fish is {new_fish['rarity']}", inline=False)
            embed.add_field(name='Cost', value=f"This fish is {new_fish['cost']}", inline=False)
            embed.color = {
                # 0xHexCode
                "common": 0xFFFFFE,  # White - FFFFFF doesn't work with Discord
                "uncommon": 0x75FE66,  # Green
                "rare": 0x4AFBEF,  # Blue
                "epic": 0xE379FF,  # Light Purple
                "legendary": 0xFFE80D,  # Gold
                "mythic": 0xFF0090,  # Hot Pink
            }[new_fish['rarity']]
            fish_file = discord.File(new_fish["image"], "new_fish.png")
            await ctx.send(file=fish_file, embed=embed)

    def create_bucket_embed(self, user, field):
        embed = discord.Embed()  # Create a new embed to edit the message
        embed.title = f"**Bestiary**\n"
        embed.add_field(name=f"__{field[0]}__", value=field[1], inline=False)
        return embed

def setup(bot):
    bot.add_cog(Bestiary(bot))
