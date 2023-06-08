import asyncio
import random
import discord
from discord.ext import vbu
from cogs import utils
import math


async def start_using(ctx, bot):

    embed = discord.Embed(title="Woah There")
    embed.add_field(
        name="Welcome to AquaMarine!",
        value="Welcome! My name is Aqua (the axolotl), and I'm here to help you get familiar with this experience. " +
              "I'm so glad you chose to take this venture with me, out to catch and collect all the fish and aquatic " +
              "species there are.")
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            discord.ui.Button(
                label="I'm glad as well! What should I do first?", custom_id="continue"),
            discord.ui.Button(
                label="Umm... Why are you a talking Axolotl?", custom_id="query_1"),
            discord.ui.Button(label="I didn't sign up for this??"),
            discord.ui.Button(label="Are there more creatures like you?"),
        )
    )
    await ctx.author.send(file=discord.File("C:\\Users\\JT\\Pictures\\Aqua\\assets\\images\\background\\aqua_idle.png"))
    await ctx.author.send(embed=embed, components=components)
