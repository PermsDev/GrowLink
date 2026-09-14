import discord

from discord import app_commands
from discord.ext import commands

from utils.guilds.guild_access import (
    require_general_access,
)


class Ping(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Check apakah GrowLink sedang online."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        if not await require_general_access(
            interaction
        ):
            return

        latency = round(
            self.bot.latency * 1000
        )

        await interaction.response.send_message(
            f"🏓 Pong! `{latency}ms`"
        )


async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Ping(bot)
    )