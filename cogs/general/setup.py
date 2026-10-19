import logging
import time

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


logger = logging.getLogger("growlink")


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
        started_at = time.monotonic()

        logger.info(
            "[Setup %s] Sending initial response. "
            "Interaction ID: %s | Created at: %s",
            command_name,
            interaction.id,
            interaction.created_at.isoformat(),
        )

        try:
            await interaction.response.send_message(
                f"⏳ Panel {command_name} sedang dibuat...",
                ephemeral=True,
            )

            elapsed = time.monotonic() - started_at

            logger.info(
                "[Setup %s] Initial response sent in %.3f seconds. "
                "Interaction ID: %s",
                command_name,
                elapsed,
                interaction.id,
            )

            return True

        except discord.NotFound:
            elapsed = time.monotonic() - started_at

            logger.exception(
                "[Setup %s] Interaction not found after %.3f seconds. "
                "Interaction ID: %s",
                command_name,
                elapsed,
                interaction.id,
            )

            return False

        except discord.HTTPException:
            elapsed = time.monotonic() - started_at

            logger.exception(
                "[Setup %s] Failed to acknowledge interaction after "
                "%.3f seconds. Interaction ID: %s",
                command_name,
                elapsed,
                interaction.id,
            )

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

            logger.info(
                "[Setup %s] Initial response edited successfully. "
                "Interaction ID: %s",
                command_name,
                interaction.id,
            )

        except discord.HTTPException:
            logger.exception(
                "[Setup %s] Failed to edit the original response. "
                "Interaction ID: %s",
                command_name,
                interaction.id,
            )

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
        callback_started_at = time.monotonic()

        logger.info(
            "[Setup Intro] Callback started. "
            "Interaction ID: %s | Created at: %s",
            interaction.id,
            interaction.created_at.isoformat(),
        )

        acknowledged = await self.acknowledge_interaction(
            interaction,
            "Intro",
        )

        logger.info(
            "[Setup Intro] Acknowledgement completed after %.3f seconds. "
            "Interaction ID: %s | Success: %s",
            time.monotonic() - callback_started_at,
            interaction.id,
            acknowledged,
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

            logger.info(
                "[Setup Intro] Panel created. "
                "Guild ID: %s | Channel ID: %s | Interaction ID: %s",
                interaction.guild.id,
                channel.id,
                interaction.id,
            )

        except Exception:
            logger.exception(
                "[Setup Intro] Failed to create the Introduction panel. "
                "Interaction ID: %s",
                interaction.id,
            )

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
        callback_started_at = time.monotonic()

        logger.info(
            "[Setup Promote] Callback started. "
            "Interaction ID: %s | Created at: %s",
            interaction.id,
            interaction.created_at.isoformat(),
        )

        acknowledged = await self.acknowledge_interaction(
            interaction,
            "Promote",
        )

        logger.info(
            "[Setup Promote] Acknowledgement completed after %.3f seconds. "
            "Interaction ID: %s | Success: %s",
            time.monotonic() - callback_started_at,
            interaction.id,
            acknowledged,
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

            logger.info(
                "[Setup Promote] Panel created. "
                "Guild ID: %s | Channel ID: %s | Interaction ID: %s",
                interaction.guild.id,
                channel.id,
                interaction.id,
            )

        except Exception:
            logger.exception(
                "[Setup Promote] Failed to create the Promote panel. "
                "Interaction ID: %s",
                interaction.id,
            )

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
