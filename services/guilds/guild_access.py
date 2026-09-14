from database.main.guilds.guild_key_manager import (
    get_guild_key,
)


# ==================================================
# CHECK GENERAL ACCESS
# ==================================================
async def is_general_guild(
    guild_id: int
) -> bool:
    """
    Mengecek apakah guild memiliki akses General.

    General:
        - General
        - Partnership
    """

    guild_key = await get_guild_key(guild_id)

    return guild_key in (
        "General",
        "Partnership"
    )


# ==================================================
# CHECK PARTNERSHIP ACCESS
# ==================================================
async def is_partnership_guild(
    guild_id: int
) -> bool:
    """
    Mengecek apakah guild memiliki akses Partnership.

    Partnership:
        - Partnership
    """

    guild_key = await get_guild_key(guild_id)

    return guild_key == "Partnership"