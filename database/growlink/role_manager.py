from database.database import get_grow_pool as get_pool


async def get_role(
    guild_id: int,
    role_key: str,
) -> int | None:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT role_id
                FROM gl_roles
                WHERE guild_id = %s
                    AND role_key = %s
                LIMIT 1
                """,
                (
                    guild_id,
                    role_key,
                ),
            )

            result = await cursor.fetchone()

            return result[0] if result else None