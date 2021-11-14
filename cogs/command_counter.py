from discord.ext import commands, vbu


class CommandCounter(vbu.Cog):

    @vbu.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """
        Count every time a command is run uwu
        """

        command = ctx.command
        if command is None:
            return
        command_name = command.name

        async with vbu.Database() as db:
            current_count = await db("SELECT count FROM command_counter WHERE command_name=$1", command_name)

            # Make sure we get a current count
            if current_count:
                current_count = current_count[0]['count']
            else:
                current_count = 0

            await db("INSERT INTO command_counter (command_name, count) VALUES ($1, $2) ON CONFLICT (command_name) DO UPDATE SET count = $2", command_name, current_count + 1)

        self.bot.logger.info(f"Logging command completion: {command.name}")

    @commands.command(aliases=['commandstats', 'commandcount', 'commandcounter'])
    async def commanddata(self, ctx: commands.Context):
        """
        Send out the list of commands and their current count
        """

        # Get info from database
        async with vbu.Database() as db:
            command_data = await db("SELECT * FROM command_counter")

        # Make sure we have data
        if not command_data:
            return await ctx.send("No command data was found in the database.")

        # Set up the command list
        sorted_commands_singlelist = []
        commands_list = {} # List of strings "**command name**: command count"
        total_count = 0 # To count the total number of commands
        for command in command_data:
            count = command['count']
            total_count += count
        for command in command_data:
            count = command['count']
            commands_list[f"**{command['command_name']}**: {count} times `({(count / total_count) * 100:.2f}%)`\n"] = count
            #commands_list.append({count: f"**{command['command_name']}**: {count} times `({(count / total_count) * 100}%)`\n"})

        sorted_commands = sorted(commands_list.items(), key=lambda x: x[1], reverse=True)
        for i in sorted_commands:
            sorted_commands_singlelist.append(i[0])
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
        pagin = vbu.Paginator(sorted_commands_singlelist, formatter=formatter, per_page=10)
        await pagin.start(ctx)



def setup(bot: vbu.Bot):
    x = CommandCounter(bot)
    bot.add_cog(x)

