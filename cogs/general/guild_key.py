import discord

from discord import app_commands
from discord.ext import commands

from database.main.guilds.guild_key_manager import (
    get_guild_key,
)

from utils.guilds.guild_access import (
    require_general_access,
)


class GuildKey(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @app_commands.command(
        name="guild-key",
        description="Mengecek guild key server ini."
    )
    async def guild_key(
        self,
        interaction: discord.Interaction
    ):

        if not await require_general_access(
            interaction
        ):
            return

        guild_key = await get_guild_key(
            interaction.guild.id
        )

        await interaction.response.send_message(
            f"🔑 Guild Key: `{guild_key}`"
        )


async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        GuildKey(bot)
    )