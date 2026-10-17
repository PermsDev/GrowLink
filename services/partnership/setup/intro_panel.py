import discord

from config.constants import INTRO_CHANNEL_KEY
from database.growlink.setup_manager import (
    get_setup,
    upsert_setup,
)

from views.partnership.introduction.introduction_view import IntroductionView

async def create_intro_panel(
    guild: discord.Guild,
    channel: discord.TextChannel,
) -> discord.Message:

    # ==================================================
    # GET PREVIOUS PANEL
    # ==================================================
    previous_setup = await get_setup(
        guild_id=guild.id,
        channel_key=INTRO_CHANNEL_KEY,
    )

    # ==================================================
    # DELETE PREVIOUS PANEL
    # ==================================================
    if previous_setup is not None:

        previous_channel_id = previous_setup["channel_id"]
        previous_message_id = previous_setup["panel_message"]

        if previous_message_id is not None:

            previous_channel = guild.get_channel(
                previous_channel_id
            )

            if previous_channel is not None:

                try:
                    previous_message = await previous_channel.fetch_message(
                        previous_message_id
                    )

                    await previous_message.delete()

                except discord.NotFound:
                    # Message sudah tidak ada.
                    pass

                except discord.Forbidden:
                    # Bot tidak memiliki permission untuk menghapus.
                    pass

    # ==================================================
    # SEND NEW PANEL
    # ==================================================
    message = await channel.send(
        embed=IntroductionView.get_embed(),
        view=IntroductionView()
    )

    # ==================================================
    # SAVE NEW PANEL
    # ==================================================
    await upsert_setup(
        guild_id=guild.id,
        channel_key=INTRO_CHANNEL_KEY,
        channel_id=channel.id,
        panel_message=message.id,
    )

    return message
