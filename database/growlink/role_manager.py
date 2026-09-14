from database.database import get_grow_pool as get_pool


ROLE_KEY = "GT_intro"


async def upsert_role(
    guild_id: int,
    role_key: str,
    role_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO gl_roles (
                    guild_id,
                    role_key,
                    role_id
                )
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    role_id = VALUES(role_id)
                """,
                (
                    guild_id,
                    role_key,
                    role_id,
                )
            )

            await conn.commit()

