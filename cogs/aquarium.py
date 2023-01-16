import discord
from discord.ext import commands, vbu
from cogs import utils


class Aquarium(vbu.Cog):
    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="tank_name",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The name you want to apply to your first tank",
                )
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True)
    async def firsttank(self, ctx: commands.Context, tank_name: str):
        """
        This command gives the user their first tank.
        """

        # See if they already have a tank
        async with vbu.Database() as db:
            fetched = await utils.user_tank_inventory_db_call(ctx.author.id)
        if fetched:
            return await ctx.send("You have your first tank already!")

        # Add a tank to the user
        async with vbu.Database() as db:
            await db(
                """INSERT INTO user_tank_inventory VALUES ($1);""",
                ctx.author.id,
            )
            await db(
                """UPDATE user_tank_inventory SET tank[1]=TRUE, tank_type[1]='Fish Bowl', tank_name[1] = $2,
                fish_room[1] = 1, tank_theme[1] = 'Aqua' WHERE user_id=$1""",
                ctx.author.id,
                tank_name,
            )
        await ctx.send(
            f"You have your new tank, **{tank_name}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(
            options=[
                discord.ApplicationCommandOption(
                    name="theme",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The theme that you want to apply to the chosen tank",
                    choices=[
                        discord.ApplicationCommandOptionChoice(
                            name="Plant Life", value="Plant_Life"
                        )
                    ],
                ),
                discord.ApplicationCommandOption(
                    name="tank_type",
                    type=discord.ApplicationCommandOptionType.string,
                    description="The type of tank chosen",
                    choices=[
                        discord.ApplicationCommandOptionChoice(
                            name="Fish Bowl", value="Fish Bowl"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Small Tank", value="Small Tank"
                        ),
                        discord.ApplicationCommandOptionChoice(
                            name="Medium Tank", value="Medium Tank"
                        ),
                    ],
                ),
            ]
        )
    )
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def preview(self, ctx: commands.Context, theme: str, tank_type: str):
        """
        Previews a tank theme
        """

        # Set up the image and display
        image = f"{utils.file_prefix}/background/tank_theme_previews/{theme}_{utils.tank_types[tank_type]}_preview.png"
        await ctx.send(file=discord.File(image))


def setup(bot):
    bot.add_cog(Aquarium(bot))
