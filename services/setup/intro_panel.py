
import discord

from config.constants import INTRO_CHANNEL_KEY
from database.growlink.setup_manager import (
    get_setup,
    upsert_setup,
)
from views.introduction.introduction_view import IntroductionView


async def create_intro_panel(
    guild: discord.Guild,
    channel: discord.TextChannel,
) -> discord.Message:
    previous_setup = await get_setup(
        guild_id=guild.id,
        channel_key=INTRO_CHANNEL_KEY,
    )

    message = await channel.send(
        embed=IntroductionView.get_embed(),
        view=IntroductionView(),
    )

    try:
        await upsert_setup(
            guild_id=guild.id,
            channel_key=INTRO_CHANNEL_KEY,
            channel_id=channel.id,
            panel_message=message.id,
        )
    except Exception:
        try:
            await message.delete()
        except discord.HTTPException:
            pass
        raise

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
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass

    return message
