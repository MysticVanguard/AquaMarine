from datetime import datetime, timedelta
import random
import time
import asyncpg
import json
with open("database_config.json") as a:
    database_config = json.load(a)

import discord
from discord.ext import commands

# Takes the token in from a txt file
with open('AquaMarineToken.txt') as aquamarine_token:
    token = aquamarine_token.readline()
# Sets global variables for the timer
duration = timedelta(seconds=20)
later = datetime.utcnow()

# Sets the prefix and makes it usable
prefix = ["A.", "a."]
bot = commands.Bot(command_prefix=prefix)

current_fishers = []
# Each fish name in a dictionary seperated by rarity
fish_types_rarity = {
    "Common": ["Goldfish", "Clownfish", "Tiger Barb", "Neon Tetra", "Oscar", "Squid", "Common Starfish", "Bottlenose Dolphin"], 
    "Uncommon": ["Lionfish", "Betta", "Blue Maomao", "Headshield Snail", "Seahorse"], 
    "Rare": ["Flowerhorn Cichlid", "Axolotl"], 
    "Epic": ["Pufferfish", "Sea Bunny"], 
    "Legendary": ["Angler"],
    "Mythic": ["Mandarinfish"]
}
# Each fish name set in a dictionary with the path for the normal file
fish_information = {
    "Goldfish": ("C:/Users/JT/Pictures/Aqua/goldfish-export", "small"), 
    "Clownfish": ("C:/Users/JT/Pictures/Aqua/Clownfish-export", "small"), 
    "Tiger Barb": ("C:/Users/JT/Pictures/Aqua/Tiger_Barb-export", "small"), 
    "Neon Tetra": ("C:/Users/JT/Pictures/Aqua/Neon_Tetra_School-export", "small"), 
    "Oscar": ("C:/Users/JT/Pictures/Aqua/Oscar_Cichlid-export", "medium"), 
    "Squid": ("C:/Users/JT/Pictures/Aqua/Squid-export", "medium"),
    "Common Starfish": ("C:/Users/JT/Pictures/Aqua/Starfish-export", "medium"),
    "Bottlenose Dolphin": ("C:/Users/JT/Pictures/Aqua/Bottlenose_Dolphin-export", "extra large"),
    "Lionfish": ("C:/Users/JT/Pictures/Aqua/Lionfish-export", "medium"), 
    "Betta": ("C:/Users/JT/Pictures/Aqua/Blue_Betta-export", "small"), 
    "Blue Maomao": ("C:/Users/JT/Pictures/Aqua/Blue_maomao-export", "medium"),
    "Headshield Snail": ("C:/Users/JT/Pictures/Aqua/Headshield_Slug-export", "tiny"),
    "Seahorse": ("C:/Users/JT/Pictures/Aqua/Seahorse-export", "medium"),
    "Flowerhorn Cichlid": ("C:/Users/JT/Pictures/Aqua/Flowerhorn_Cichlid-export", "medium"), 
    "Axolotl": ("C:/Users/JT/Pictures/Aqua/Axolotl-export", "medium"), 
    "Pufferfish": ("C:/Users/JT/Pictures/Aqua/Pufferfish-export", "medium"),
    "Sea Bunny": ("C:/Users/JT/Pictures/Aqua/Sea_Bunny-export", "tiny"),
    "Angler": ("C:/Users/JT/Pictures/Aqua/Anglerfish-export", "medium"),
    "Mandarinfish": ("C:/Users/JT/Pictures/Aqua/Mandarinfish-export", "small")
}
money_multiplier = {
    "small": 1,
    "medium": 2,
    "large": 3,
    "tiny": 5,
    "extra large": 5,
    "Common": 10,
    "Uncommon": 50,
    "Rare": 250,
    "Epic": 1250,
    "Legendary": 6250,
    "Mythic": 1000000
}
database_auth = database_config["database"]
class DatabaseConnection(object):

    def __init__(self, conn=None):
        self.conn = conn

    async def connect(self):
        self.conn = await asyncpg.connect(**database_auth)

    async def disconnect(self):
        await self.conn.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def __call__(self, sql, *args):
        return await self.conn.fetch(sql, *args)
bot.database_auth = database_auth 
bot.database = DatabaseConnection

# Tells you when the bot is started up
@bot.event
async def on_ready():
    print("Everything's all ready to go~")

@bot.event
async def on_message(message):
    print("The message's content was", message.content)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''

    # Get the latency of the bot
    latency = bot.latency  
    # Send it to the user
    await ctx.send(latency)

# Echo's what the user types after the command
@bot.command()
async def echo(ctx, *, content:str):
    await ctx.send(content)

def fish_pricer(fish_name, fish_rarity_name):
    fish_price = money_multiplier[fish_information[fish_name][1]] * money_multiplier[fish_rarity_name]
    return fish_price
    
# Function that determines which fish is caught out of rarity, and if it's special
async def fishing_rarity(ctx, fish_rarity_name, chancespecial):
    fish_rarity = fish_types_rarity[fish_rarity_name]
    fish_name = random.choice(fish_rarity)
    # Adds certain strings to the end of the file based on chancespecial
    if chancespecial >= 6:
        new_fish_name = fish_name
        file_path = ".png"   
    elif chancespecial >= 1:
        new_fish_name = "Inverted " + fish_name
        file_path = "_inverted.png"
    elif chancespecial >= 0:
        new_fish_name = "Golden " + fish_name
        file_path = "_golden.png"
    await ctx.send(f"You caught {fish_rarity_name}: {new_fish_name}!", file=discord.File(fish_information[fish_name][0] + file_path))
    await ctx.send("Do you want to keep or sell your fish?")
    def check(message):
        valid_responses = ["keep", "sell"]
        return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in valid_responses
    user_input = await bot.wait_for('message', check=check)
    if user_input.content.lower() == "keep":
        await ctx.send("What do you want to name your fish?")
        def naming(message):
            return message.author == ctx.author and message.channel == ctx.channel
        user_input = await bot.wait_for('message', check=naming)
        current_fishers.remove(ctx.author.id)
        async with bot.database() as db:
            await db("INSERT INTO user_fish_inventory (user_id, fish, fish_name) VALUES ($1,$2, $3)", ctx.author.id, new_fish_name, user_input.content)
        await ctx.send(f"You now have \"{user_input.content}\", your {new_fish_name}!")
    elif user_input.content.lower() == "sell":
        async with bot.database() as db:
            current_fishers.remove(ctx.author.id)
            bal_rows = await db("SELECT * FROM user_balance WHERE user_id=$1", ctx.author.id)
            bal = fish_pricer(fish_name, fish_rarity_name)
            if bal_rows:
                total_bal = bal_rows[0]['balance'] + bal
            else:
                total_bal = bal
            await db("INSERT INTO user_balance (user_id, balance) VALUES ($1,$2) ON CONFLICT (user_id) DO UPDATE SET balance = $2", ctx.author.id, total_bal)
        await ctx.send(f"You sold {new_fish_name} for {bal}!")

@bot.command()
async def balance(ctx):
    async with bot.database() as db:
        bal_rows = await db("SELECT * FROM user_balance WHERE user_id=$1", ctx.author.id)

    if bal_rows:
        await ctx.send(f"You have {bal_rows[0]['balance']} money!")
    else:
        await ctx.send("You have no money!")

@bot.command()
async def fishbucket(ctx):
    async with bot.database() as db:
        fish_rows = await db("SELECT * FROM user_fish_inventory WHERE user_id=$1", ctx.author.id)
    if not fish_rows:
        return await ctx.send("You have no fish!")
    fish_list = [f"\"{i['fish_name']}\", {i['fish']}" for i in fish_rows]
    await ctx.send(f"You have the following fish: {'; '.join(fish_list)}")

# Fishing command
@bot.command()
async def fish(ctx):
    global duration
    global later
    # Sets now to be when the command happens, then checks if its after later 
    now = datetime.utcnow()
    

    if now >= later:
        # Determines chances, and sets later
        chance = random.randint(0, 9999)
        chance_special = random.randint(0, 99)
        later = now + duration
        if ctx.author.id in current_fishers:
            return await ctx.send("You're already fishing!")
        current_fishers.append(ctx.author.id)

        # Decides which rarity the fish will be based on chance
        if chance == 9999:
            await fishing_rarity(ctx, "Mythic", chance_special)
        elif chance >= 9936:
            await fishing_rarity(ctx, "Legendary", chance_special)
        elif chance >= 9732:
            await fishing_rarity(ctx, "Epic", chance_special)
        elif chance >= 9072:
            await fishing_rarity(ctx, "Rare", chance_special)
        elif chance >= 6932:
            await fishing_rarity(ctx, "Uncommon", chance_special)
        elif chance >= 0:
            await fishing_rarity(ctx, "Common", chance_special)
    else:
        # If the timer isn't up, it tells the user to wait and how long to wait
        remaining = round((later - datetime.utcnow()).total_seconds())
        await ctx.send("Please wait " + str(remaining) + " seconds.")
        print(remaining)

# Get's github link     
@bot.command()
async def git(ctx):
    await ctx.send("https://github.com/MysticVanguard/AquaMarine")


bot.load_extension("jishaku")
bot.run(token)


