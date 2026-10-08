from database.database import get_grow_pool as get_pool


async def add_phishing_image(
    sha256: str,
    phash: str,
    discord_user_id: int | None = None,
    guild_id: int | None = None,
    source: str = "discord",
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO phishing_image (
                    sha256,
                    phash,
                    discord_user_id,
                    guild_id,
                    source
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    sha256,
                    phash,
                    discord_user_id,
                    guild_id,
                    source,
                ),
            )

            await conn.commit()

            return cursor.lastrowid


async def get_by_sha256(
    sha256: str,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_image
                WHERE sha256 = %s
                LIMIT 1
                """,
                (sha256,),
            )

            return await cursor.fetchone()


async def get_by_id(
    image_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_image
                WHERE id = %s
                LIMIT 1
                """,
                (image_id,),
            )

            return await cursor.fetchone()


async def get_active_images():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_image
                WHERE status = 'active'
                ORDER BY id ASC
                """
            )

            return await cursor.fetchall()


async def get_all_phishing_images():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_image
                ORDER BY id ASC
                """
            )

            return await cursor.fetchall()


async def update_status(
    image_id: int,
    status: str,
):
    if status not in (
        "active",
        "inactive",
    ):
        raise ValueError(
            "Invalid phishing image status."
        )

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE phishing_image
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    image_id,
                ),
            )

            await conn.commit()

            return cursor.rowcount > 0