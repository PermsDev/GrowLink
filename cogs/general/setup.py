import discord
from discord import app_commands
from discord.ext import commands

from config.constants import (
    INTRO_ROLE_KEY,
    FEATURE_INTRODUCTION,
    FEATURE_PROMOTION,
)

from services.setup.intro_panel import create_intro_panel
from services.setup.promote_panel import create_promote_panel

from database.growlink.role_manager import upsert_role
from database.growlink.feature_manager import set_feature_active


class SetupGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="setup",
            description="Configure GrowLink features.",
            default_permissions=discord.Permissions(administrator=True),
        )

    async def interaction_check(
        self,
        interaction: discord.Interaction,
    ) -> bool:
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True,
            )
            return False

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Only administrators can use this command.",
                ephemeral=True,
            )
            return False

        return True


class Setup(commands.Cog):
    setup_group = SetupGroup()

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def acknowledge_interaction(
        self,
        interaction: discord.Interaction,
        command_name: str,
    ) -> bool:
        try:
            await interaction.response.send_message(
                f"⏳ Panel {command_name} sedang dibuat...",
                ephemeral=True,
            )
            return True

        except discord.NotFound:
            return False

        except discord.HTTPException:
            return False

    async def send_result(
        self,
        interaction: discord.Interaction,
        message: str,
        command_name: str,
    ) -> None:
        try:
            await interaction.edit_original_response(
                content=message,
                embed=None,
                view=None,
            )
        except discord.HTTPException:
            pass

    @setup_group.command(
        name="intro",
        description="Create the Introduction panel.",
    )
    @app_commands.describe(
        channel="Channel where the Introduction panel will be posted.",
        role="Role assigned after completing the Introduction.",
    )
    async def intro(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role | None = None,
    ):
        acknowledged = await self.acknowledge_interaction(
            interaction,
            "Intro",
        )

        if not acknowledged:
            return

        try:
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
                    role_key=INTRO_ROLE_KEY,
                    role_id=role.id,
                )

            await self.send_result(
                interaction,
                f"✅ Introduction panel created in {channel.mention}.",
                "Intro",
            )

        except Exception:
            await self.send_result(
                interaction,
                "❌ Failed to create the Introduction panel. "
                "Check the bot logs.",
                "Intro",
            )

    @setup_group.command(
        name="promote",
        description="Create the Promote panel.",
    )
    @app_commands.describe(
        channel="Channel where the Promote panel will be posted.",
    )
    async def promote(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ):
        acknowledged = await self.acknowledge_interaction(
            interaction,
            "Promote",
        )

        if not acknowledged:
            return

        try:
            await create_promote_panel(
                guild=interaction.guild,
                channel=channel,
            )

            await set_feature_active(
                guild_id=interaction.guild.id,
                feature_type=FEATURE_PROMOTION,
                active=True,
            )

            await self.send_result(
                interaction,
                f"✅ Promote panel created in {channel.mention}.",
                "Promote",
            )

        except Exception:
            await self.send_result(
                interaction,
                "❌ Failed to create the Promote panel. "
                "Check the bot logs.",
                "Promote",
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))

    if bot.tree.get_command("setup") is None:
        bot.tree.add_command(Setup.setup_group)
