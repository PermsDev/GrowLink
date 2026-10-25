
import discord
from discord import app_commands
from discord.ext import commands

from views.help.help_view import HelpView


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_commands(self) -> list[app_commands.Command]:
        result = []

        for command in self.bot.tree.walk_commands():
            if not isinstance(command, app_commands.Command):
                continue

            if command.qualified_name == "help":
                continue

            result.append(command)

        return sorted(
            result,
            key=lambda command: command.qualified_name,
        )

    async def command_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        current = current.strip().lower()

        matches = [
            command
            for command in self.get_commands()
            if current in command.qualified_name.lower()
        ]

        return [
            app_commands.Choice(
                name=command.qualified_name[:100],
                value=command.qualified_name,
            )
            for command in matches[:25]
        ]

    @app_commands.command(
        name="help",
        description="View the usage guide for GrowLink commands.",
    )
    @app_commands.describe(
        command="The command you want to learn about."
    )
    @app_commands.autocomplete(command=command_autocomplete)
    async def help_command(
        self,
        interaction: discord.Interaction,
        command: str,
    ):
        available_commands = {
            item.qualified_name
            for item in self.get_commands()
        }

        if command not in available_commands:
            await interaction.response.send_message(
                "Command not found.",
                ephemeral=True,
            )
            return

        view = HelpView(command)

        await interaction.response.send_message(
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
