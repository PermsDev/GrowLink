import discord

from services.guilds.guild_access import (
    is_general_guild,
    is_partnership_guild,
)


# ==================================================
# REQUIRE GENERAL ACCESS
# ==================================================
async def require_general_access(
    interaction: discord.Interaction
) -> bool:
    """
    Mengecek akses General.

    Return:
        True  -> memiliki akses
        False -> tidak memiliki akses
    """

    if await is_general_guild(interaction.guild.id):
        return True

    await interaction.response.send_message(
        "❌ Server ini tidak terdaftar di GrowLink.",
        ephemeral=True
    )

    return False


# ==================================================
# REQUIRE PARTNERSHIP ACCESS
# ==================================================
async def require_partnership_access(
    interaction: discord.Interaction
) -> bool:
    """
    Mengecek akses Partnership.

    Return:
        True  -> memiliki akses
        False -> tidak memiliki akses
    """

    if await is_partnership_guild(interaction.guild.id):
        return True

    await interaction.response.send_message(
        "❌ Server ini tidak memiliki akses Partnership GrowLink.",
        ephemeral=True
    )

    return False