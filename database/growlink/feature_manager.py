from database.database import get_grow_pool as get_pool


# ==================================================
# FEATURE TYPES
# ==================================================

FEATURE_INTRODUCTION = "introduction"


# ==================================================
# GET FEATURE
# ==================================================

async def get_feature_id(
    feature_type: str
) -> int | None:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT feature_id
                FROM gl_feature
                WHERE feature_type = %s
                LIMIT 1
                """,
                (feature_type,)
            )

            row = await cursor.fetchone()

            if row is None:
                return None

            return int(row[0])


# ==================================================
# ENSURE FEATURE
# ==================================================

async def ensure_feature(
    feature_type: str
) -> int:

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT feature_id
                FROM gl_feature
                WHERE feature_type = %s
                LIMIT 1
                """,
                (feature_type,)
            )

            row = await cursor.fetchone()

            if row is not None:
                return int(row[0])

            await cursor.execute(
                """
                INSERT INTO gl_feature (
                    feature_type
                )
                VALUES (%s)
                """,
                (feature_type,)
            )

            await conn.commit()

            return int(cursor.lastrowid)


# ==================================================
# SET FEATURE ACTIVE
# ==================================================

async def set_feature_active(
    guild_id: int,
    feature_type: str,
    active: bool = True,
):

    feature_id = await ensure_feature(
        feature_type
    )

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO gl_feature_active (
                    guild_id,
                    feature_id,
                    active
                )
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    active = VALUES(active)
                """,
                (
                    guild_id,
                    feature_id,
                    "1" if active else "0",
                )
            )

            await conn.commit()


# ==================================================
# GET FEATURE ACTIVE
# ==================================================

async def is_feature_active(
    guild_id: int,
    feature_type: str,
) -> bool:

    feature_id = await get_feature_id(
        feature_type
    )

    if feature_id is None:
        return False

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT active
                FROM gl_feature_active
                WHERE guild_id = %s
                  AND feature_id = %s
                LIMIT 1
                """,
                (
                    guild_id,
                    feature_id,
                )
            )

            row = await cursor.fetchone()

            if row is None:
                return False

            return row[0] == "1"
        
        
# ==================================================
# GET ACTIVE FEATURE GUILD IDs (Khusus fitur introduction)
# ==================================================

async def get_active_feature_guild_ids(feature_id: int = 1) -> list[int]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT guild_id
                FROM gl_feature_active
                WHERE feature_id = %s
                AND active = '1'
                """,
                (feature_id,),
            )

            rows = await cursor.fetchall()

    return [int(row[0]) for row in rows]
