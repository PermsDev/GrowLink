import discord

from database.main.user.display_name_manager import (
    get_display_source,
    set_display_source,
    set_display_source_bulk,
)
from database.main.user.intro_manager import (
    get_introduction,
)


# ==================================================
# GET MEMBER DISPLAY SOURCE
# ==================================================

async def get_member_display_source(
    guild_id: int,
    user_id: int
):
    return await get_display_source(
        guild_id=guild_id,
        user_id=user_id
    )


# ==================================================
# SET GROWID DISPLAY SOURCE
# ==================================================

async def set_growid_display_source(
    guild_id: int,
    user_id: int
):
    await set_display_source(
        guild_id=guild_id,
        user_id=user_id,
        display_source="growid"
    )


# ==================================================
# SYNC GUILD MEMBERS TO GROWID
# ==================================================

async def sync_guild_members_to_growid(
    guild: discord.Guild
):
    user_ids = [
        member.id
        for member in guild.members
        if not member.bot
    ]

    if not user_ids:
        return 0

    return await set_display_source_bulk(
        guild_id=guild.id,
        user_ids=user_ids,
        display_source="growid"
    )


# ==================================================
# UPDATE DISCORD DISPLAY NAME
# ==================================================

async def update_member_display_name(
    member: discord.Member
):
    """
    Mengubah nickname Discord berdasarkan
    display_source milik user.

    Return:
        "updated"       -> berhasil mengubah
        "already_same"  -> nickname sudah sama
        "no_source"     -> display_source tidak ditemukan
        "no_data"       -> data display name tidak tersedia
        "role_too_low"  -> role bot terlalu rendah
    """

    guild_id = member.guild.id
    user_id = member.id

    # ======================
    # GET DISPLAY SOURCE
    # ======================

    display_source = await get_display_source(
        guild_id=guild_id,
        user_id=user_id
    )

    if not display_source:
        return "no_source"

    # ======================
    # GET INTRODUCTION
    # ======================

    nickname, growid = await get_introduction(
        user_id=user_id
    )

    # ======================
    # RESOLVE DISPLAY NAME
    # ======================

    display_name = None

    if display_source == "nickname":
        display_name = nickname

    elif display_source == "growid":
        display_name = growid

    if not display_name:
        return "no_data"

    # ======================
    # ALREADY SAME
    # ======================

    if member.nick == display_name:
        return "already_same"

    # ======================
    # CHECK BOT ROLE
    # ======================

    bot_member = member.guild.me

    if bot_member is None:
        return "role_too_low"

    if member.top_role >= bot_member.top_role:
        return "role_too_low"

    # ======================
    # UPDATE NICKNAME
    # ======================

    await member.edit(
        nick=display_name,
        reason="GrowLink Introduction display name"
    )

    return "updated"
