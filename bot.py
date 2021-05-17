import toml
import discord
import utils
from discord.ext import commands


with open("./config/config.toml") as f:
    config = toml.loads(f.read())

bot = commands.AutoShardedBot(
    command_prefix = config["command_prefix"],
    case_sensitive = config["case_sensitive"],
    owner_ids = config["owner_ids"],
    activity = discord.Activity(
        type = discord.ActivityType.watching,
        name = config["activity"],
        ),
    )

bot.fish = utils.fetch_fish(config["assets"]["images"]["fish"])

@bot.event
async def on_ready():
    print("Everything's all ready to go~")

if __name__ == '__main__':
    for extension in config["initial_extensions"]:
        bot.load_extension(extension)
    bot.run(config["bot_token"], reconnect=True)
