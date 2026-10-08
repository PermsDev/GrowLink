from database.database import get_grow_pool as get_pool


async def add_phishing_review(
    phishing_review_action_id: int,
    sha256: str,
    phash: str,
    similarity: float,
    matched_image_id: int | None = None,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO phishing_review (
                    phishing_review_action_id,
                    sha256,
                    phash,
                    similarity,
                    matched_image_id
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    phishing_review_action_id,
                    sha256,
                    phash,
                    similarity,
                    matched_image_id,
                ),
            )

            await conn.commit()

            return cursor.lastrowid


async def get_review_by_id(
    review_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_review
                WHERE id = %s
                LIMIT 1
                """,
                (review_id,),
            )

            return await cursor.fetchone()


async def update_review_status(
    review_id: int,
    status: str,
):
    if status not in (
        "pending",
        "approved",
        "rejected",
    ):
        raise ValueError(
            "Invalid review status."
        )

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE phishing_review
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    review_id,
                ),
            )

            await conn.commit()

            return cursor.rowcount > 0


async def add_review_action(
    message_id: int,
    action: str,
    guild_id: int | None = None,
    channel_id: int | None = None,
    reported_user_id: int | None = None,
    reporter_user_id: int | None = None,
    reviewer_user_id: int | None = None,
):
    if action not in (
        "reported",
        "punished",
    ):
        raise ValueError(
            "Invalid review action."
        )

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO phishing_review_action (
                    guild_id,
                    message_id,
                    channel_id,
                    reported_user_id,
                    reporter_user_id,
                    reviewer_user_id,
                    action
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    guild_id,
                    message_id,
                    channel_id,
                    reported_user_id,
                    reporter_user_id,
                    reviewer_user_id,
                    action,
                ),
            )

            await conn.commit()

            return cursor.lastrowid


async def update_review_message_id(
    action_id: int,
    review_message_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE phishing_review_action
                SET review_message_id = %s
                WHERE id = %s
                """,
                (
                    review_message_id,
                    action_id,
                ),
            )

            await conn.commit()

            return cursor.rowcount > 0


async def update_review_action_to_punished(
    action_id: int,
    reviewer_user_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE phishing_review_action
                SET
                    action = 'punished',
                    reviewer_user_id = %s
                WHERE id = %s
                  AND action = 'reported'
                """,
                (
                    reviewer_user_id,
                    action_id,
                ),
            )

            await conn.commit()

            return cursor.rowcount > 0


async def get_report_action_by_message_id(
    message_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_review_action
                WHERE message_id = %s
                  AND action = 'reported'
                ORDER BY id ASC
                LIMIT 1
                """,
                (message_id,),
            )

            return await cursor.fetchone()


async def get_report_action_by_review_id(
    review_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    pra.id,
                    pra.guild_id,
                    pra.message_id,
                    pra.review_message_id,
                    pra.channel_id,
                    pra.reported_user_id,
                    pra.reporter_user_id,
                    pra.reviewer_user_id,
                    pra.action
                FROM phishing_review_action pra
                INNER JOIN phishing_review pr
                    ON pr.phishing_review_action_id = pra.id
                WHERE pr.id = %s
                LIMIT 1
                """,
                (review_id,),
            )

            return await cursor.fetchone()


async def get_review_action_by_id(
    action_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_review_action
                WHERE id = %s
                LIMIT 1
                """,
                (action_id,),
            )

            return await cursor.fetchone()


async def get_pending_review_actions():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT DISTINCT pra.*
                FROM phishing_review_action pra
                INNER JOIN phishing_review pr
                    ON pr.phishing_review_action_id = pra.id
                WHERE pra.action = 'reported'
                  AND pra.review_message_id IS NOT NULL
                  AND pr.status = 'pending'
                ORDER BY pra.id ASC
                """
            )

            return await cursor.fetchall()

async def get_review_actions_for_restore():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    guild_id,
                    message_id,
                    review_message_id,
                    channel_id,
                    reported_user_id,
                    reporter_user_id,
                    reviewer_user_id,
                    action
                FROM phishing_review_action
                WHERE review_message_id IS NOT NULL
                  AND action = 'reported'
                ORDER BY id ASC
                """
            )

            return await cursor.fetchall()

async def get_reviews_by_action_id(
    action_id: int,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                """
                SELECT *
                FROM phishing_review
                WHERE phishing_review_action_id = %s
                ORDER BY id ASC
                """,
                (action_id,),
            )

            return await cursor.fetchall()