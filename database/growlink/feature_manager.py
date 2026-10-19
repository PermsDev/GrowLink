from database.database import get_grow_pool as get_pool

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
# GET ACTIVE FEATURE GUILD IDs
# ==================================================


async def get_active_feature_guild_ids(feature_type: str) -> list[int]:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT gfa.guild_id
                FROM gl_feature_active AS gfa
                INNER JOIN gl_feature AS gf
                    ON gf.feature_id = gfa.feature_id
                WHERE gf.feature_type = %s
                  AND gfa.active = '1'
                """,
                (feature_type,),
            )

            rows = await cursor.fetchall()

    return [int(row[0]) for row in rows]

async def deactivate_feature(
    guild_id: int,
    feature_type: str,
) -> None:
    feature_id = await get_feature_id(feature_type)

    if feature_id is None:
        return

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE gl_feature_active
                SET active = '0'
                WHERE guild_id = %s
                  AND feature_id = %s
                """,
                (
                    guild_id,
                    feature_id,
                ),
            )

            await conn.commit()