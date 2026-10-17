import discord

from discord import app_commands
from discord.ext import commands

from config.constants import INTRO_ROLE_KEY

from utils.guilds.guild_access import require_partnership_access

from services.partnership.setup.intro_panel import create_intro_panel
from services.partnership.setup.promote_panel import create_promote_panel

from database.growlink.role_manager import upsert_role

from database.growlink.feature_manager import (
    set_feature_active,
    FEATURE_INTRODUCTION,
)

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
        # if not await require_partnership_access(interaction):
        #     return

        await interaction.response.defer(ephemeral=True)

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

        await interaction.followup.send(
            f"✅ Introduction panel created in {channel.mention}.",
            ephemeral=True,
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
        # if not await require_partnership_access(interaction):
        #     return

        await interaction.response.defer(ephemeral=True)

        await create_promote_panel(
            guild=interaction.guild,
            channel=channel,
        )

        await interaction.followup.send(
            f"✅ Promote panel created in {channel.mention}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))

    if bot.tree.get_command("setup") is None:
        bot.tree.add_command(Setup.setup_group)
