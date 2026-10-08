import discord

from discord import app_commands
from discord.ext import commands

from services.phishing.report_service import (
    report_message,
)


class PhishingReportCog(
    commands.Cog
):

    def __init__(
        self,
        bot: commands.Bot,
    ):
        self.bot = bot

        self.report_command = (
            app_commands.ContextMenu(
                name="Report Phishing",
                callback=self.report,
            )
        )

        self.bot.tree.add_command(
            self.report_command
        )

    async def report(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ):

        await report_message(
            bot=self.bot,
            interaction=interaction,
            message=message,
        )

    def cog_unload(self):

        self.bot.tree.remove_command(
            self.report_command.name,
            type=self.report_command.type,
        )


async def setup(
    bot: commands.Bot,
):

    await bot.add_cog(
        PhishingReportCog(bot)
    )