import discord

from database.growlink.feature_manager import (
    FEATURE_INTRODUCTION,
    is_feature_active,
)

from services.partnership.display_name.display_name_service import (
    sync_guild_members_to_growid,
)


# ==================================================
# SYNC INTRODUCTION DISPLAY NAME
# ==================================================

async def sync_introduction_display_name(
    guild: discord.Guild
):
    """
    Mengecek apakah feature Introduction aktif.

    Jika aktif:
        Sync seluruh member guild
        menjadi display_source = 'growid'.

    Jika tidak aktif:
        Tidak melakukan sync.

    Return:
        int: jumlah member yang di-sync.
        0 jika feature tidak aktif.
    """

    active = await is_feature_active(
        guild_id=guild.id,
        feature_type=FEATURE_INTRODUCTION,
    )

    if not active:
        return 0

    return await sync_guild_members_to_growid(
        guild
    )
