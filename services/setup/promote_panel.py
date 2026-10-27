import discord

from config.constants import PROMOTE_CHANNEL_KEY
from database.growlink.setup_manager import (
    get_setup,
    upsert_setup,
)
from database.growlink.webhook_manager import (
    replace_channel_webhook,
)
from views.promote.promote_view import PromoteView


async def create_promote_panel(
    bot: discord.Client,
    guild: discord.Guild,
    channel: discord.TextChannel,
) -> discord.Message:
    if channel.guild.id != guild.id:
        raise ValueError("Channel does not belong to this guild.")

    previous_setup = await get_setup(
        guild_id=guild.id,
        channel_key=PROMOTE_CHANNEL_KEY,
    )

    if previous_setup is not None:
        previous_channel_id = int(previous_setup["channel_id"])
        previous_message_id = previous_setup["panel_message"]

        if previous_message_id is not None:
            previous_channel = guild.get_channel(previous_channel_id)

            if previous_channel is None:
                try:
                    fetched_channel = await bot.fetch_channel(
                        previous_channel_id
                    )
                    if (
                        isinstance(fetched_channel, discord.TextChannel)
                        and fetched_channel.guild.id == guild.id
                    ):
                        previous_channel = fetched_channel
                except (
                    discord.NotFound,
                    discord.Forbidden,
                ):
                    previous_channel = None

            if isinstance(previous_channel, discord.TextChannel):
                try:
                    previous_message = await previous_channel.fetch_message(
                        int(previous_message_id)
                    )
                    await previous_message.delete()

                except (
                    discord.NotFound,
                    discord.Forbidden,
                ):
                    pass

    webhook = await replace_channel_webhook(
        bot=bot,
        channel=channel,
    )

    bot_user = bot.user

    message = await webhook.send(
        view=PromoteView(),
        username=bot_user.name if bot_user else "GrowLink",
        avatar_url=(
            bot_user.display_avatar.url
            if bot_user
            else discord.utils.MISSING
        ),
        allowed_mentions=discord.AllowedMentions.none(),
        wait=True,
    )

    await upsert_setup(
        guild_id=guild.id,
        channel_key=PROMOTE_CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=message.id,
    )

    return message
