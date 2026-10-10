import discord

from discord import app_commands
from discord.ext import commands

from utils.guilds.guild_access import (
    require_partnership_access,
)

from services.partnership.setup.intro_panel import (
    create_intro_panel,
)

from database.growlink.role_manager import (
    upsert_role,
    ROLE_KEY,
)

from database.growlink.feature_manager import (
    set_feature_active,
    FEATURE_INTRODUCTION,
)


class SetupIntro(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot

    @app_commands.default_permissions(administrator=True)
    @app_commands.command(
        name="setup-intro",
        description="Membuat panel Introduction."
    )
    @app_commands.describe(
        channel="Channel untuk menampilkan panel Introduction.",
        role="Role yang akan diberikan setelah Introduction."
    )
    async def setup_intro(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role | None = None,
    ):
        # if not await require_partnership_access(
        #     interaction
        # ):
        #     return

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Hanya administrator yang dapat menggunakan command ini.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        await create_intro_panel(
            guild=interaction.guild,
            channel=channel,
        )

        await set_feature_active(
            guild_id=interaction.guild.id,
            feature_type=FEATURE_INTRODUCTION,
            active=True,
        )

        if role is not None:
            await upsert_role(
                guild_id=interaction.guild.id,
                role_key=ROLE_KEY,
                role_id=role.id,
            )

        await interaction.followup.send(
            f"✅ Panel Introduction berhasil dibuat di {channel.mention}.",
            ephemeral=True
        )


async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        SetupIntro(bot)
    )