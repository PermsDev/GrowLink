
import discord
from asyncmy.cursors import DictCursor

from database.database import get_grow_pool as get_pool


TABLE_NAME = "gl_webhooks"


async def get_webhook_by_channel(channel_id: int) -> dict | None:
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT id, guild_id, channel_id, webhook_id,
                       webhook_token, created_at, updated_at
                FROM gl_webhooks
                WHERE channel_id = %s
                LIMIT 1
                """,
                (channel_id,),
            )
            return await cursor.fetchone()


async def save_webhook(
    guild_id: int,
    channel_id: int,
    webhook: discord.Webhook,
) -> None:
    if not webhook.token:
        raise ValueError("Webhook token is unavailable.")

    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO gl_webhooks (
                    guild_id,
                    channel_id,
                    webhook_id,
                    webhook_token
                )
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    guild_id = VALUES(guild_id),
                    webhook_id = VALUES(webhook_id),
                    webhook_token = VALUES(webhook_token)
                """,
                (
                    guild_id,
                    channel_id,
                    webhook.id,
                    webhook.token,
                ),
            )
        await conn.commit()


async def ensure_channel_webhook(
    bot: discord.Client,
    channel: discord.TextChannel,
) -> discord.Webhook:
    """
    Return an existing usable webhook or create and save a new one.
    """

    if channel.guild is None:
        raise ValueError("The channel must belong to a guild.")

    saved = await get_webhook_by_channel(channel.id)

    if saved:
        webhook_id = saved["webhook_id"]
        webhook_token = saved["webhook_token"]

        if webhook_id and webhook_token:
            webhook_url = (
                f"https://discord.com/api/webhooks/"
                f"{webhook_id}/{webhook_token}"
            )

            try:
                webhook = discord.Webhook.from_url(
                    webhook_url,
                    client=bot,
                )

                await webhook.fetch()
                return webhook

            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException,
            ):
                pass

    webhook = await channel.create_webhook(
        name="GrowLink",
        reason="Create or refresh GrowLink channel webhook",
    )

    await save_webhook(
        guild_id=channel.guild.id,
        channel_id=channel.id,
        webhook=webhook,
    )

    return webhook
