import discord

from database.growlink.emoji_manager import get_emoji
from views.promote.promotion.review_button import (
    EditPromotionButton,
    SubmitPromotionButton,
)


class PromotionReviewView(discord.ui.LayoutView):
    def __init__(self, world_name: str, description: str):
        super().__init__(timeout=300)

        self.world_name = world_name
        self.description = description
        self.review_message = None

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    f"## {get_emoji('digi')} Review Your Promotion"
                ),
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    f"**World Name:** {self.world_name or 'Not provided'}"
                ),
                discord.ui.TextDisplay(
                    f"**Description:**\n{self.description}"
                ),
                accent_colour=discord.Color.green(),
            )
        )

        self.add_item(
            discord.ui.ActionRow(
                EditPromotionButton(self),
                SubmitPromotionButton(self),
            )
        )

    async def update_review(self, world_name: str, description: str):
        self.world_name = world_name
        self.description = description

        self.clear_items()

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    f"## {get_emoji('digi')} Review Your Promotion"
                ),
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    f"**World Name:** {self.world_name or 'Not provided'}"
                ),
                discord.ui.TextDisplay(
                    f"**Description:**\n{self.description}"
                ),
                accent_colour=discord.Color.green(),
            )
        )

        self.add_item(
            discord.ui.ActionRow(
                EditPromotionButton(self),
                SubmitPromotionButton(self),
            )
        )

        if self.review_message:
            await self.review_message.edit(view=self)