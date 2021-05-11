from datetime import datetime, timedelta
import random
import time

import discord
from discord.ext import commands


with open('AquaMarineToken.txt') as aquamarine_token:
    token = aquamarine_token.readline()
duration = timedelta(minutes=0)
later = datetime.utcnow()


prefix = "A."
bot = commands.Bot(command_prefix=prefix)
fish_types_rarity = [
    ["Goldfish", "Clownfish", "Tiger Barb", "Neon Tetra", "Oscar", "Squid", "Common Starfish", "Bottlenose Dolphin"], 
    ["Lionfish", "Betta", "Blue Maomao", "Headshield Snail"], 
    ["Flowerhorn Cichlid", "Axolotl"], 
    ["Pufferfish", "Sea Bunny"], 
    ["Angler"],
    ["Mandarinfish"]
]
fishing_paths = {
    "Goldfish": "C:/Users/JT/Pictures/Aqua/goldfish-export", 
    "Clownfish": "C:/Users/JT/Pictures/Aqua/Clownfish-export", 
    "Tiger Barb": "C:/Users/JT/Pictures/Aqua/Tiger_Barb-export", 
    "Neon Tetra": "C:/Users/JT/Pictures/Aqua/Neon_Tetra_School-export", 
    "Oscar": "C:/Users/JT/Pictures/Aqua/Oscar_Cichlid-export", 
    "Squid": "C:/Users/JT/Pictures/Aqua/Squid-export",
    "Common Starfish": "C:/Users/JT/Pictures/Aqua/Starfish-export",
    "Bottlenose Dolphin": "C:/Users/JT/Pictures/Aqua/Bottlenose_Dolphin-export",
    "Lionfish": "C:/Users/JT/Pictures/Aqua/Lionfish-export", 
    "Betta": "C:/Users/JT/Pictures/Aqua/Blue_Betta-export", 
    "Blue Maomao": "C:/Users/JT/Pictures/Aqua/Blue_maomao-export",
    "Headshield Snail": "C:/Users/JT/Pictures/Aqua/Headshield_Slug-export",
    "Flowerhorn Cichlid": "C:/Users/JT/Pictures/Aqua/Flowerhorn_Cichlid-export", 
    "Axolotl": "C:/Users/JT/Pictures/Aqua/Axolotl-export", 
    "Pufferfish": "C:/Users/JT/Pictures/Aqua/Pufferfish-export",
    "Sea Bunny": "C:/Users/JT/Pictures/Aqua/Sea_Bunny-export",
    "Angler": "C:/Users/JT/Pictures/Aqua/Anglerfish-export",
    "Mandarinfish": "C:/Users/JT/Pictures/Aqua/Mandarinfish-export"
}


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
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)

@bot.command()
async def echo(ctx, *, content:str):
    await ctx.send(content)


async def fishing_rarity(ctx, fish_rarity_value, chancespecial):
    fish_rarity = fish_types_rarity[fish_rarity_value]
    fish_name = random.choice(fish_rarity)
    if chancespecial >= 6:
        await ctx.send(f"You caught {fish_name}!", file=discord.File(fishing_paths[fish_name] + ".png"))
    elif chancespecial >= 1:
        await ctx.send(f"You caught Inverted {fish_name}!", file=discord.File(fishing_paths[fish_name] + "_inverted.png"))
    elif chancespecial >= 0:
        await ctx.send(f"You caught Golden {fish_name}!", file=discord.File(fishing_paths[fish_name] + "_golden.png"))

@bot.command()
async def fish(ctx):
    global duration
    global later
    now = datetime.utcnow()
    

    if now >= later:
        
        chance = random.randint(0, 9999)
        chance_special = random.randint(0, 100)
        later = now + duration

       
        if chance == 9999:
            await fishing_rarity(ctx, 5, chance_special)
        elif chance >= 9936:
            await fishing_rarity(ctx, 4, chance_special)
        elif chance >= 9732:
            await fishing_rarity(ctx, 3, chance_special)
        elif chance >= 9072:
            await fishing_rarity(ctx, 2, chance_special)
        elif chance >= 6932:
            await fishing_rarity(ctx, 1, chance_special)
        elif chance >= 0:
            await fishing_rarity(ctx, 0, chance_special)
    else:
        remaining = round((later - datetime.utcnow()).total_seconds())
        await ctx.send("Please wait " + str(remaining) + " seconds.")
        print(remaining)
           




bot.run(token)


