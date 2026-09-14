from database.database import get_main_pool as get_pool


VALID_GUILD_KEYS = {
    "General",
    "Partnership",
}


# ==================================================
# GET GUILD KEY
# ==================================================
async def get_guild_key(
    guild_id: int
) -> str | None:
    """
    Mengambil guild_key GrowLink yang valid.

    Return:
        General
        Partnership
        None
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT guild_key
                FROM guild_key_db
                WHERE guild_id = %s
                  AND guild_key IN ('General', 'Partnership')
                LIMIT 1
            """, (
                guild_id,
            ))

            row = await cursor.fetchone()

    if row is None:
        return None

    return row[0]

# ==================================================
# GET ALL GENERAL GUILD IDS
# ==================================================
async def get_general_guild_ids() -> list[int]:
    """
    Mengambil semua guild_id yang memiliki
    guild_key = General.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT guild_id
                FROM guild_key_db
                WHERE guild_key = 'General'
            """)

            rows = await cursor.fetchall()

    return [
        row[0]
        for row in rows
    ]
    
    
# ==================================================
# ADD GUILD KEY
# ==================================================
async def add_guild_key(
    guild_id: int
) -> None:
    """
    Menambahkan guild ke sistem GrowLink.

    Guild baru otomatis memiliki:
        General

    Jika guild sudah memiliki key,
    data tidak akan ditambahkan ulang.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO guild_key_db (
                    guild_id,
                    guild_key
                )
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    guild_id = guild_id
            """, (
                guild_id,
                "General"
            ))


# ==================================================
# SET GUILD KEY
# ==================================================
async def set_guild_key(
    guild_id: int,
    guild_key: str
) -> None:
    """
    Mengubah guild key.

    Valid:
        General
        Partnership

    Guild dapat berpindah:
        General -> Partnership
        Partnership -> General
    """

    if guild_key not in VALID_GUILD_KEYS:
        raise ValueError(
            f"Guild key tidak valid: {guild_key}"
        )

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                UPDATE guild_key_db
                SET guild_key = %s
                WHERE guild_id = %s
            """, (
                guild_key,
                guild_id
            ))


# ==================================================
# REMOVE GUILD KEY
# ==================================================
async def remove_guild_key(
    guild_id: int
) -> None:
    """
    Menghapus guild key dari guild.

    Setelah dihapus, guild tidak lagi
    dianggap sebagai guild GrowLink.
    """

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM guild_key_db
                WHERE guild_id = %s
            """, (
                guild_id,
            ))


# ==================================================
# CHECK GROWLINK GUILD
# ==================================================
async def is_growlink_guild(
    guild_id: int
) -> bool:
    """
    Mengecek apakah guild memiliki
    guild key GrowLink yang valid.
    """

    return await get_guild_key(
        guild_id
    ) is not None
    