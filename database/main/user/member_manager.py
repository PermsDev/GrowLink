from database.database import get_main_pool as get_pool


# ==================================================
# ENSURE MEMBER
# ==================================================

async def ensure_member(
    user_id: int,
    nickname: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO member_db (
                    user_id,
                    nickname
                )
                VALUES (%s, %s) AS new
                ON DUPLICATE KEY UPDATE
                    nickname = new.nickname
            """, (
                user_id,
                nickname
            ))

        await conn.commit()


# ==================================================
# GET MEMBER
# ==================================================

async def get_member(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    nickname,
                    created_at,
                    updated_at
                FROM member_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            return await cursor.fetchone()


# ==================================================
# GET NICKNAME
# ==================================================

async def get_member_nickname(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT nickname
                FROM member_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

            row = await cursor.fetchone()

            if not row:
                return None

            return row[0]


# ==================================================
# UPDATE NICKNAME
# ==================================================

async def update_member_nickname(
    user_id: int,
    nickname: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                UPDATE member_db
                SET nickname = %s
                WHERE user_id = %s
            """, (
                nickname,
                user_id
            ))

        await conn.commit()


# ==================================================
# DELETE MEMBER
# ==================================================

async def delete_member(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM member_db
                WHERE user_id = %s
            """, (
                user_id,
            ))

        await conn.commit()