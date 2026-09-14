from asyncmy.cursors import DictCursor

from database.database import get_grow_pool as get_pool


# ==================================================
# GET SETUP
# ==================================================
async def get_setup(
    guild_id: int,
    channel_key: str
) -> dict | None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:

            await cursor.execute("""
                SELECT
                    guild_id,
                    channel_key,
                    channel_id,
                    panel_message
                FROM gl_setup
                WHERE guild_id = %s
                  AND channel_key = %s
                LIMIT 1
            """, (
                guild_id,
                channel_key
            ))

            return await cursor.fetchone()


# ==================================================
# GET CHANNEL ID
# ==================================================
async def get_channel_id(
    guild_id: int,
    channel_key: str
) -> int | None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT channel_id
                FROM gl_setup
                WHERE guild_id = %s
                  AND channel_key = %s
                LIMIT 1
            """, (
                guild_id,
                channel_key
            ))

            row = await cursor.fetchone()

            if row is None:
                return None

            return row[0]


# ==================================================
# GET PANEL MESSAGE
# ==================================================
async def get_panel_message(
    guild_id: int,
    channel_key: str
) -> int | None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT panel_message
                FROM gl_setup
                WHERE guild_id = %s
                  AND channel_key = %s
                LIMIT 1
            """, (
                guild_id,
                channel_key
            ))

            row = await cursor.fetchone()

            if row is None:
                return None

            return row[0]


# ==================================================
# CHECK SETUP EXISTS
# ==================================================
async def setup_exists(
    guild_id: int,
    channel_key: str
) -> bool:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT 1
                FROM gl_setup
                WHERE guild_id = %s
                  AND channel_key = %s
                LIMIT 1
            """, (
                guild_id,
                channel_key
            ))

            return await cursor.fetchone() is not None


# ==================================================
# CREATE / UPDATE SETUP
# ==================================================
async def upsert_setup(
    guild_id: int,
    channel_key: str,
    channel_id: int,
    panel_message: int | None = None
) -> None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO gl_setup (
                    guild_id,
                    channel_key,
                    channel_id,
                    panel_message
                )
                VALUES (%s, %s, %s, %s)
                
                ON DUPLICATE KEY UPDATE
                    channel_id = VALUES(channel_id),
                    panel_message = VALUES(panel_message)
            """, (
                guild_id,
                channel_key,
                channel_id,
                panel_message
            ))


# ==================================================
# UPDATE PANEL MESSAGE
# ==================================================
async def update_panel_message(
    guild_id: int,
    channel_key: str,
    panel_message: int | None
) -> None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                UPDATE gl_setup
                SET panel_message = %s
                WHERE guild_id = %s
                  AND channel_key = %s
            """, (
                panel_message,
                guild_id,
                channel_key
            ))


# ==================================================
# DELETE SETUP
# ==================================================
async def delete_setup(
    guild_id: int,
    channel_key: str
) -> None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM gl_setup
                WHERE guild_id = %s
                  AND channel_key = %s
            """, (
                guild_id,
                channel_key
            ))
