from PIL import Image
import random
import string
from cogs import utils
import discord


async def tanks_background_image_creator(ctx, tank_rows):
    # A dict of the positions of where glass should go for each type of tank in each spot
    position_glass = {
        "Fish Bowl": [
            (390, 160),
            (1470, 160),
            (2510, 160),
            (390, 640),
            (1470, 640),
            (2510, 640),
            (950, 1170),
            (1970, 1170),
            (950, 1540),
            (1970, 1540),
        ],
        "Small Tank": [
            (350, 40),
            (1400, 40),
            (2450, 40),
            (350, 520),
            (1400, 520),
            (2450, 520),
            (890, 1050),
            (1900, 1050),
            (809, 1440),
            (1900, 1440),
        ],
        "Medium Tank": [
            (240, 40),
            (1290, 40),
            (2340, 40),
            (240, 520),
            (1290, 520),
            (2340, 520),
            (770, 1050),
            (1780, 1050),
            (770, 1440),
            (1780, 1440),
        ],
    }

    # A dict of the positions of where themes should go for each type of tank in each spot
    position_theme = {
        "Fish Bowl": [
            (390, 160),
            (1470, 160),
            (2510, 160),
            (390, 640),
            (1470, 640),
            (2510, 640),
            (950, 1170),
            (1970, 1170),
            (950, 1540),
            (1970, 1540),
        ],
        "Small Tank": [
            (360, 70),
            (1410, 70),
            (2460, 70),
            (360, 550),
            (1410, 550),
            (2460, 550),
            (900, 1080),
            (1910, 1080),
            (900, 1470),
            (1910, 1470),
        ],
        "Medium Tank": [
            (250, 70),
            (1300, 70),
            (2350, 70),
            (250, 550),
            (1300, 550),
            (2350, 550),
            (780, 1080),
            (1790, 1080),
            (780, 1470),
            (1790, 1470),
        ],
    }

    # Random ID for what the tank will be saved as
    id = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
    )

    # Set the unique file name for the wall
    file_name = f"{utils.file_prefix}/background/Room Walls/Tanks_Wall/User Walls/{id}user_tank_room.png"

    # Open the background image for tanks to be pasted onto and copy it
    background = Image.open(
        f"{utils.file_prefix}/background/Room Walls/Tank_Wall-export.png"
    ).convert("RGBA")
    new_background = background.copy()

    # For each tank...
    for slot, tank in enumerate(tank_rows[0]["tank_type"]):

        # If theres nothing dont change anything
        if tank == "":
            continue

        # Set start and theme_raise to 0 for tanks under the counter
        start = ""
        theme_raise = 0

        # If its a medium or small tank and in the spots under the counter
        if (tank == "Medium Tank" or tank == "Small Tank") and slot in [
            10,
            11,
        ]:
            # Change the start and the raise of the theme
            start = "Under_"
            theme_raise = 2

        # Set the type to what it is, the positions of the glass and theme to what they are, and the theme to what it is for this tank
        tank_type = utils.tank_types[tank]
        x_and_y_glass = position_glass[tank][slot]
        x_and_y_theme = position_theme[tank][slot]
        if tank_rows:
            tank_theme = tank_rows[0]["tank_theme"][slot].replace(" ", "_")

            # Open the glass and theme images
            glass = Image.open(
                f"{utils.file_prefix}/background/Room Walls/Tanks_Wall/{start}Glass_{tank_type}-export.png"
            ).convert("RGBA")
            theme = Image.open(
                f"{utils.file_prefix}/background/Room Walls/Tanks_Wall/{tank_theme}_{tank_type}-export.png"
            ).convert("RGBA")

            # Paste them on top of the background
            new_background.paste(
                theme, (x_and_y_theme[0], x_and_y_theme[1]), theme)
            new_background.paste(
                glass,
                (x_and_y_glass[0], x_and_y_glass[1] - theme_raise),
                glass,
            )

    # save the file as a png
    new_background.save(file_name, format="PNG")

    # Send the file
    await ctx.send(file=discord.File(file_name))


GUIDE_FIELDS = [
    ("Table of Contents", "Fishing - page 2\n" "Aquariums and Fish Care - page 5\n"),
    (
        "Guide to Fishing",
        "When you fish, various things can occur. The most likely thing that will happen "
        "is you will catch a fish. This fish will be a certain rarity (common, uncommon, rare, "
        "epic, legendary, mythic), a certain size (small, medium, large), a certain type of fish "
        "(100+ different types) and skinned (purely cosmetic part). \nThe rarity determines how rare "
        "the fish is to catch, and the base cost it sells for (5, 15, 75, 375, 750, 5000). Rarer fish "
        "will also give more when the tank they are in is cleaned, which will be talked about more later. "
        "\nThe size of the fish determines how many size points it takes up (1, 5, 25) in a tank, which will "
        "also be talked about more later. It also determines the multiplier to the base cost (1x, 2x, 3x). "
        "This means that a small common fish will sell for 5, while a large common fish would sell for 15. "
        "\nThe type of fish is just what kind of fish your getting, and the type has a set rarity and size. "
        "The skin is just cosmetic and there is a small chance of getting a skinned fish, almost like a shiny. "
        "\n\tWhen you use the `fish` command, a picture of what fish you caught will pop up as well as 4 buttons, "
        "each with the name of a different fish in the bot. If you choose the correct button that matches with the "
        "shown fish, you'll get bonus money (15 + (base rarity / 10).\n\tNow when you catch a fish, you can choose "
        "to either keep or sell this fish. Keeping the fish will pull up a form and you would enter what you want to "
        "name the fish, and adds it to your bucket, while selling the fish will instead get rid of it, and add money "
        "to your balance (base rarity * (size multiplier + rod upgrade multiplier + vote multiplier) is the equation). "
        'You\'ll also be shown some other information in the format of: \n"User caught a/an *rarity* __skin__ size **fish name**!" '
        "\n**owned/unowned** (tells you if you own atleast one of the fish)\nYou have x **fish name** (tells you how many "
        "(x) exactly of that fish you have)\nIf you don't respond with keep or sell it will automatically sell the fish, "
        "and if you don't respond with a fish name after keeping, it will give it a random generated name (which can "
        "later be renamed with the `rename` command).\n\n\tThe next thing you can get while fishing is trash. "
        "Trash is pretty useful to be honest, as it can be crafted into different things using the `craft` command. "
        "Trash has a 1 in 12 chance of appearing on a cast, and you can catch between 1 and 6 pieces.\n\n\tThe last "
        "thing you can catch is a crate, which can only be caught in addition to a fish. This crate can contain "
        "many different things depending on the crate tier upgrade, but the things it could contain are "
        "sand dollars, casts, fish bags, food, and potions.",
    ),
    (
        "Guide to Aquariums and Fish Care",
        "The first part of having aquariums is geting your first one. To get an aquarium, simply run "
        "`firsttank` command, which will give you your first tank for free. There are currently three "
        "tiers of tanks (fish bowl, small tank, medium tank), and they each have different size point "
        "values (1, 5, 25), which should be taken into consideration based on the fish you want to "
        "put into them, as the fish have certain size points they take up. \nTo deposit a fish "
        'simply use the "`deposit` fish name" command, where fish name is the name of the fish '
        "you want to deposit, and it will bring up a select menu with all of your tanks. Choose "
        "the tank you want to deposit it in and then your set, except the fish will die in three days. "
        "\n\nDon't worry, as this timer can be extended by feeding your fish. There are three types "
        "of fish food, flakes, pellets, and wafers. These each feed a different level of fish, "
        "and have increasing costs, making it more expensive to feed higher level fish. Each food type "
        "adds 3 days to a fish's lifespan when they are fed, which will stack. You can also buy a "
        "feeding potion, which will give your fish 30 days added. \nNow that you know how to keep "
        "your fish alive, you can focus on making money from it. The main way to make money from "
        "tanks is to clean them, which is has a couple factors going into the pay. First there is "
        "the effort bonus which will add either 0, 15, or 30 to the total cost (weighted randomness). "
        "Then the rest is based off of the fish in the tank, and for each fish it takes their level "
        "* (rarity multiplier (common - 1.0, uncommon - 1.2, rare -1.4, epic - 1.6, "
        "legendary - 1.8, mythic - 2.0) + size multiplier (small - 0, medium - 2, large - 14)) and adds "
        "them all together. Then it takes that value * (bleach upgrade multiplier + vote multiplier + "
        "hygeinic upgrade multiplier) and then adds the effort bonus. Out of all this, the big takeaway "
        "is that the fish's level and rarity are important factors, and the higher they are, the more "
        "you will get from cleaning tanks. \nThe last of the three fish care topics is entertaining. "
        "You can entertain all the fish in a specific tank, and it will take a set amount of xp (based "
        "off of your toys upgrade), and then split that between every fish in the tank. This is set up "
        "in a way so that you can funnel a lot more xp into a single fish if you choose to, but you end "
        "up with 24 lost size points if its small (bigger fish give less money when cleaned helping make "
        "this funneling not as advantagous). If you're just a casual player and just want to collect fish, "
        "you probably would just want to go at things normally with whatever fish you want in your tanks. "
        "\n\nAs mentioned previously, there is a `deposit` command which will add a specified fish to a tank. "
        "There is also a `remove` command which will remove a specified fish from whatever tank it is in. "
        "Removing a fish sets its death timer to nothing, meaning that you could get out of feeding that fish "
        "by removing it right before it needed fed. Because of this, now you must feed your fish right before "
        "removing it, no matter the death timer.\nIf you want to see your tank and what fish are in it you "
        "can use the `show` command and it will produce a gif (might take a few seconds). You also may "
        "notice there are tank themes for sale, which when bought, a tank is specified and it's basically "
        "a skin for your tank, and is purely cosmetic. You can preview any of these themes by using the "
        "`preview` command with the name of the theme, and it will produce a drop down where you can pick "
        "the type of tank.\nThe last thing I will mention in this section is the `revive` command, which "
        "simple enough, revives one of your dead fish. You have to have a revival, which can be bought "
        "from the store. ",
    ),
]

help_descriptions = {
    "prefix": (
        "prefix *new prefix*",
        "This command will change the prefix of the bot in your server.",
    ),
    "info": (
        "info",
        "This command will show various info about the bot, including a little blurb on how to use it, and some useful buttons (a button to invite the bot, "
        "the website one doesn't work, one to the support server, one to the github, the donate one doesn't work, and one to vote for the bot).",
    ),
    "invite": ("invite", "This will give the invite link for the bot."),
    "vote": (
        "vote",
        "This will give a link to top.gg, where you can vote to unlock a 1.5x bonus to gained sand dollars and access to the daily command for that day.",
    ),
    "stats": (
        "stats",
        "This command will show various info about the bot, including the creator, votes, and guild (server) count.",
    ),
    "firsttank": (
        "firsttank",
        "This command needs to be used before you can have a tank, and it will give you your first starter tank with 1 point of space.",
    ),
    "preview": (
        "preview *theme*",
        "This command will preview the given theme, on the tank type (chosen after via select box).",
    ),
    "fish": (
        "fish",
        "This command is the most basic command, and is used to catch a fish, that can be kept or sold. First it will have you guess the name of a fish for a "
        "few bonus sand dollars, then you can choose to keep the fish, where you wil lthen have to name it, or you can choose to sell the fish to get more sand dollars.",
    ),
    "rename": (
        'rename "*old fish/tank\'s name*" "*new fish/tank\'s name*"',
        "This command will let you rename a fish or tank to a new name, prioritizing the tank name if there is both a fish and tank with the name.",
    ),
    "craft": (
        "craft __item name__",
        "This command will give a menu (when no item name is supplied) of what items can be crafted, what they do, and how much trash it costs to craft them. "
        "If an item name is supplied, it will try to craft the item.",
    ),
    "tank": (
        "tank *tank name*",
        "This command will show a few buttons to help manage your tank. The first button entertains the fish inside, giving them xp. "
        "The second button cleans the tank, giving you money. The third button will give a drop down of hungry fish in the tank, and let you feed one of them if you "
        "have fish food for them, adding 3 days to their lifespan. The revive button can be used to revive a fish if you have a revival, giving a dropdown of dead "
        "fish in the tank. The show button will create a gif of the fish swimming in the tank (if they are alive). The remove fish button will remove a fish from the "
        "tank, but make sure you have some fish food on you as it will take up one of them to remove the fish. The deposit fish button will deposit a fish into the tank "
        "if there is room in the tank. The info button will give info on the tank like its type, the room left, and info on the fish inside",
    ),
    "stab": (
        "stab *mention user*",
        "This command will send a cute gif and stab another user.",
    ),
    "bug": (
        "bug *command name* *report of problem*",
        "This command can be used to report any problems you see in the bot that you don't think are intentional.",
    ),
    "support": (
        "support",
        "This command will give a link to the support server for the bot, where there is a growing community and cute aqua emotes.",
    ),
    "shop": (
        "shop",
        "This command sends a paginated embed of the shop, with various items for sale.",
    ),
    "buy": (
        'buy "*item*" __amount__',
        "This command is used to buy an amount of an item that is listed in the shop.",
    ),
    "use": (
        "use *item*",
        "This command uses an item, either a fish bag or a potion. If a fish bag is used, it is relatively similar to using the 'fish' command. If a potion is used, a name "
        "of the fish it is given to will need to be entered.",
    ),
    "inventory": (
        "inventory",
        "This command will show you how many of each different item you have.",
    ),
    "balance": (
        "balance __user mention__",
        "This command will show your balance, or a mentioned user's balance if one's given.",
    ),
    "sell": (
        "sell *fish name*",
        "This command will sell a fish, increasing with the level of fish sold.",
    ),
    "daily": (
        "daily",
        "This command will let you spin a wheel of prizes of voted, where you can win up to 4,800 sand dollars.",
    ),
    "gamble": (
        "gamble *amount divisible by 100*",
        "This command let's you gamble and win or lose your sand dollars.",
    ),
    "upgrades": (
        "upgrades",
        "This will show your progression in upgrades, each giving various buffs and bonuses. The previous upgrade must be fully upgrade before the next tier is unlocked.",
    ),
    "upgrade": (
        "upgrade *upgrade name*",
        "This will upgrade the given upgrade by one if you have enough sand dollars to do so.",
    ),
    "tanks": (
        "tanks",
        "This will show various info on all the tanks you have, and the fish inside them.",
    ),
    "profile": (
        "profile",
        "This will show a lot of compact info about you, including your highest level fish, how many unique different types of fish you have, sorted by rarity, how many of each "
        "item you have, how many tanks you have, and your balance.",
    ),
    "bestiary": (
        "bestiary __fish name__",
        "This command will give a paginated embed of every fish name sorted by rarity, or if a specific fish is given, it will show what that fish looks like, it's size, and how "
        "much it sells for.",
    ),
    "fishbucket": (
        "fishbucket __user mention__",
        "This command will give you a paginated embed of all the fish you have kept, giving info about their name, size, if they are alive, and if they have a skin.",
    ),
    "achievements": (
        "achievements",
        "This command shows you various achievements that can be collected and your progress. If there are claimable rewards, a button will appear (This command may need ran "
        "multiple times to claim all rewards).",
    ),
    "leaderboard": (
        "leaderboard",
        "This command will open up a dropdown where you will choose the type of leaderboard you want to view (balance, fish points), and then give the leaderboard in the selected "
        "area. Balance is everyone's current balance, and fish points are directly related to the fish a user has kept.",
    ),
    "guide": (
        "guide",
        "This command is used to learn how to use the bot, and explains the commands and interworkings of the bot much more in depth.",
    ),
    "totalfish": (
        "totalfish",
        "This command is used to see a ranking of the most kept fish in the bot to the least kept fish.",
    ),
    "help": (
        "help __command__",
        "This command gives general info on each command, or specific info on a singular command if one is specified.",
    ),
}
