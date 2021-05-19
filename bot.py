import discord
import utils
from discord.ext import commands

bot = commands.AutoShardedBot(
    command_prefix = utils.config["command_prefix"],
    case_sensitive = utils.config["case_sensitive"],
    owner_ids = utils.config["owner_ids"],
    activity = discord.Activity(
        type = discord.ActivityType.watching,
        name = utils.config["activity"],
        ),
    )

bot.fish = utils.fetch_fish()
bot.config = utils.config

@bot.event
async def on_ready():
    print("Everything's all ready to go~")

if __name__ == '__main__':
    for extension in utils.config["initial_extensions"]:
        bot.load_extension(extension)
    bot.run(utils.config["bot_token"], reconnect=True)