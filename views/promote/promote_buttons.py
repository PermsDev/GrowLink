import logging
import time

import discord

from database.growlink.emoji_manager import get_emoji
from views.promote.promotion.promotion_modal import PromoteModal
from views.promote.information.views import PromoteInformationView

logger = logging.getLogger(__name__)


class PromoteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Promote Item / World",
            emoji=get_emoji("megaphone"),
            style=discord.ButtonStyle.success,
            custom_id="growlink:promote:start",
        )
        
    async def callback(self, interaction: discord.Interaction):
        import time

        started = time.monotonic()
        print(f"[Promote] Callback started: {interaction.id}")

        try:
            modal = PromoteModal()
            print(
                f"[Promote] Modal constructed in "
                f"{time.monotonic() - started:.3f}s"
            )

            await interaction.response.send_modal(modal)

            print(
                f"[Promote] Modal opened in "
                f"{time.monotonic() - started:.3f}s"
            )
        except discord.HTTPException as error:
            print(
                f"[Promote] Failed after "
                f"{time.monotonic() - started:.3f}s: {error}"
            )

class PromoteInformationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Information",
            emoji=get_emoji("guide"),
            style=discord.ButtonStyle.secondary,
            custom_id="growlink:promote:info",
        )

    async def callback(self, interaction: discord.Interaction):
        await PromoteInformationView.send(interaction)