from database.database import get_main_pool as get_pool


# ==================================================
# GET INTRODUCTION
# ==================================================

async def get_introduction(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    m.nickname,
                    g.value
                FROM member_db AS m
                LEFT JOIN game_db AS g
                    ON g.user_id = m.user_id
                    AND g.game_key = 'growtopia'
                WHERE m.user_id = %s
            """, (
                user_id,
            ))

            row = await cursor.fetchone()

            if not row:
                return None, None

            return row[0], row[1]


# ==================================================
# SAVE INTRODUCTION
# ==================================================

async def save_introduction(
    user_id: int,
    nickname: str,
    growid: str
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:

            async with conn.cursor() as cursor:

                # ==================================
                # MEMBER
                # ==================================

                await cursor.execute("""
                    INSERT INTO member_db (
                        user_id,
                        nickname
                    )
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                        nickname = VALUES(nickname)
                """, (
                    user_id,
                    nickname
                ))

                # ==================================
                # GROWID
                # ==================================

                await cursor.execute("""
                    INSERT INTO game_db (
                        user_id,
                        game_key,
                        value
                    )
                    VALUES (%s, 'growtopia', %s)
                    ON DUPLICATE KEY UPDATE
                        value = VALUES(value)
                """, (
                    user_id,
                    growid
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise