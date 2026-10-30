from database.database import get_grow_pool as get_pool
from asyncmy.cursors import DictCursor


EMOJIS = {}

async def load_emojis():
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute("""
                SELECT
                    emoji_key,
                    emoji_id,
                    animated
                FROM gl_emoji
            """)

            rows = await cursor.fetchall()

    EMOJIS.clear()

    for row in rows:
        emoji_key = row["emoji_key"]

        EMOJIS[emoji_key.lower()] = {
            "emoji_key": emoji_key,
            "emoji_id": row["emoji_id"],
            "animated": bool(row["animated"]),
        }


async def reload_emojis():
    await load_emojis()


def get_emojis():
    return {
        emoji["emoji_key"]: {
            "emoji_id": emoji["emoji_id"],
            "animated": emoji["animated"],
        }
        for emoji in EMOJIS.values()
    }


def get_emoji_id(emoji_key: str):
    emoji = EMOJIS.get(emoji_key.lower())

    if not emoji:
        return None

    return emoji["emoji_id"]


def get_emoji(emoji_key: str, default: str = "🎯"):
    emoji = EMOJIS.get(emoji_key.lower())

    if not emoji:
        return default

    original_key = emoji["emoji_key"]
    emoji_id = emoji["emoji_id"]

    if emoji["animated"]:
        return f"<a:{original_key}:{emoji_id}>"

    return f"<:{original_key}:{emoji_id}>"


async def set_emoji(
    emoji_key: str,
    emoji_id: int,
    animated: bool,
):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO gl_emoji (
                        emoji_key,
                        emoji_id,
                        animated
                    )
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        emoji_id = VALUES(emoji_id),
                        animated = VALUES(animated)
                """, (
                    emoji_key,
                    emoji_id,
                    animated,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise

    EMOJIS[emoji_key.lower()] = {
        "emoji_key": emoji_key,
        "emoji_id": emoji_id,
        "animated": bool(animated),
    }


async def delete_emoji(emoji_key: str):
    pool = get_pool()

    async with pool.acquire() as conn:
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    DELETE FROM gl_emoji
                    WHERE LOWER(emoji_key) = LOWER(%s)
                """, (
                    emoji_key,
                ))

            await conn.commit()

        except Exception:
            await conn.rollback()
            raise

    EMOJIS.pop(emoji_key.lower(), None)