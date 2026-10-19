import discord

from config.constants import PROMOTE_CHANNEL_KEY

from database.growlink.setup_manager import (
    get_setup,
    upsert_setup,
)

from views.promote.promote_view import PromoteView


async def create_promote_panel(
    guild: discord.Guild,
    channel: discord.TextChannel,
) -> discord.Message:

    previous_setup = await get_setup(
        guild_id=guild.id,
        channel_key=PROMOTE_CHANNEL_KEY,
    )

    if previous_setup is not None:
        previous_channel_id = previous_setup["channel_id"]
        previous_message_id = previous_setup["panel_message"]

        if previous_message_id is not None:
            previous_channel = guild.get_channel(previous_channel_id)

            if previous_channel is not None:
                try:
                    previous_message = await previous_channel.fetch_message(
                        previous_message_id
                    )
                    await previous_message.delete()

                except (discord.NotFound, discord.Forbidden):
                    pass

    message = await channel.send(
        view=PromoteView(),
    )

    await upsert_setup(
        guild_id=guild.id,
        channel_key=PROMOTE_CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=message.id,
    )

    return message
