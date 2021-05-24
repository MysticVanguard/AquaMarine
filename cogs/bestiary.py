import discord
import utils
import random
import asyncio
import typing
from discord.ext import commands

class Bestiary(commands.Cog):
    def __init__(self, bot:commands.AutoShardedBot):
        self.bot = bot

    