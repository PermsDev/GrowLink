import discord

from database.growlink.emoji_manager import get_emoji
from views.promote.promotion.review_button import (
    EditPromotionButton,
    SubmitPromotionButton,
)
from views.promote.promotion.emoji_list_button import EmojiListButton


class PromotionReviewView(discord.ui.LayoutView):
    def __init__(self, world_name: str, description: str):
        super().__init__(timeout=300)

        self.world_name = world_name
        self.description = description
        self.review_message = None

        self.build_view()

    def build_view(self):
        self.clear_items()

        word_count = len(self.description.split())
        if word_count < 3:
            self.add_item(
                discord.ui.TextDisplay(
                    "⚠️ **Description Too Short**\n"
                    "Your promotion description must contain at least "
                    "3 words. Please edit it before submitting."
                )
            )

        container_items = [
            discord.ui.TextDisplay(
                f"## {get_emoji('digi')} Review Your Promotion"
            ),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(
                f"**World Name:** {self.world_name or 'Not provided'}"
            ),
        ]

        container_items.append(
            discord.ui.TextDisplay(
                f"**Description:**\n{self.description}"
            )
        )

        self.add_item(
            discord.ui.Container(
                *container_items,
                accent_colour=discord.Color.green(),
            )
        )

        self.add_item(
            discord.ui.ActionRow(
                EditPromotionButton(self),
                SubmitPromotionButton(self),
            )
        )

        self.add_item(
            discord.ui.ActionRow(
                EmojiListButton(),
            )
        )

    async def update_review(self, world_name: str, description: str):
        self.world_name = world_name
        self.description = description

        self.build_view()

        if self.review_message:
            await self.review_message.edit(view=self)