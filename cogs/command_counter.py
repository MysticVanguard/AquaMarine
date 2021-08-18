import voxelbotutils as vbu


class CommandCounter(vbu.Cog):

    @vbu.Cog.listener()
    async def on_command_completion(self, ctx: vbu.Context):
        """
        Count every time a command is run uwu
        """

        command = ctx.command
        command_name = command.name

        async with self.bot.database() as db:
            current_count = await db("SELECT count FROM command_counter WHERE command_name=$1", command_name)
            current_count = current_count[0]['count']

            await db("INSERT INTO command_counter (command_name, count) VALUES ($1, $2) ON CONFLICT command_name DO SET count = $2", command_name, current_count + 1)

        self.bot.logger.info(f"Logging command completion: {ctx.command.name}")

    @vbu.command(aliases=['commandstats', 'commandcount', 'commandcounter'])
    async def commanddata(self, ctx: vbu.Context):
        """
        Send out the list of commands and their current count
        """

        # Get info from database
        async with self.bot.database() as db:
            command_data = await db("SELECT * FROM command_counter")

        # Make sure we have data
        if not command_data:
            await ctx.send("No command data was found in the database.")

        # Set up the command list
        commands_list = [] # List of strings "**command name**: command count"
        total_count = 0 # To count the total number of commands
        for command in command_data:
            count = command['count']
            total_count += count
            commands_list.append(f"**{command['command_name']}**: {count} times\n")

        # Paginate

        # Set up the paginator formatter
        def formatter(menu, items):
            # Create the embed
            commands_embed = vbu.Embed(title = "Command Data (times run)")
            # Add the total count footer
            commands_embed.set_footer(text=f"Total: {total_count}")
            # Add the command list to the emebd
            commands_embed.description = "\n".join(items)

            # Return the embed
            return commands_embed

        # Begin paginating
        pagin = vbu.Paginator(commands_list, formatter=formatter, per_page=10)
        await pagin.start(ctx)



def setup(bot: vbu.Bot):
    x = CommandCounter(bot)
    bot.add_cog(x)

