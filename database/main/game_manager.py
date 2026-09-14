from database.database import get_main_pool as get_pool


VALID_GAME_KEYS = {
    "growtopia",
    "mlbb",
    "roblox"
}


# ==================================================
# VALIDATE GAME KEY
# ==================================================

def validate_game_key(
    game_key: str
):
    if game_key not in VALID_GAME_KEYS:
        raise ValueError(
            f"Invalid game_key: {game_key}"
        )


# ==================================================
# ENSURE GAME
# ==================================================

async def ensure_game(
    user_id: int,
    game_key: str,
    value: str | None = None
):
    validate_game_key(game_key)

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO game_db (
                    user_id,
                    game_key,
                    value
                )
                VALUES (%s, %s, %s) AS new
                ON DUPLICATE KEY UPDATE
                    value = new.value
            """, (
                user_id,
                game_key,
                value
            ))

        await conn.commit()


# ==================================================
# GET GAME
# ==================================================

async def get_game(
    user_id: int,
    game_key: str
):
    validate_game_key(game_key)

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    game_key,
                    value,
                    created_at,
                    updated_at
                FROM game_db
                WHERE user_id = %s
                  AND game_key = %s
            """, (
                user_id,
                game_key
            ))

            return await cursor.fetchone()


# ==================================================
# GET GAME VALUE
# ==================================================

async def get_game_value(
    user_id: int,
    game_key: str
):
    validate_game_key(game_key)

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT value
                FROM game_db
                WHERE user_id = %s
                  AND game_key = %s
            """, (
                user_id,
                game_key
            ))

            row = await cursor.fetchone()

            if not row:
                return None

            return row[0]


# ==================================================
# GET ALL GAMES
# ==================================================

async def get_all_games(
    user_id: int
):
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    user_id,
                    game_key,
                    value,
                    created_at,
                    updated_at
                FROM game_db
                WHERE user_id = %s
                ORDER BY game_key
            """, (
                user_id,
            ))

            return await cursor.fetchall()


# ==================================================
# UPDATE GAME
# ==================================================

async def update_game(
    user_id: int,
    game_key: str,
    value: str | None
):
    validate_game_key(game_key)

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                UPDATE game_db
                SET value = %s
                WHERE user_id = %s
                  AND game_key = %s
            """, (
                value,
                user_id,
                game_key
            ))

        await conn.commit()


# ==================================================
# DELETE GAME
# ==================================================

async def delete_game(
    user_id: int,
    game_key: str
):
    validate_game_key(game_key)

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM game_db
                WHERE user_id = %s
                  AND game_key = %s
            """, (
                user_id,
                game_key
            ))

        await conn.commit()