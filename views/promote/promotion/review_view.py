import discord

from database.growlink.emoji_manager import get_emoji
from views.promote.promotion.review_button import (
    EditPromotionButton,
    SubmitPromotionButton,
    EmojiListButton,
)


class PromotionReviewView(discord.ui.LayoutView):
    def __init__(
        self,
        world_name: str,
        description: str,
        submitter: discord.abc.User,
    ):
        super().__init__(timeout=900)

        self.world_name = world_name
        self.description = description
        self.submitter = submitter
        self.review_message = None

        self.build_view()

    def build_view(self):
        self.clear_items()

        word_count = len(self.description.split())

        if word_count < 2:
            self.add_item(
                discord.ui.TextDisplay(
                    "⚠️ **Description Too Short**\n"
                    "Your promotion description must contain at least "
                    "2 words. Please edit it before submitting."
                )
            )

        container_items = [
            discord.ui.TextDisplay(
                f"## {get_emoji('digi')} Review Promotion"
            ),
            discord.ui.Separator(visible=True),
        ]

        if self.world_name and self.world_name.strip():
            container_items.extend(
                [
                    discord.ui.TextDisplay(
                        f"**{get_emoji('globe')} WORLD AT: **"
                        f"`{self.world_name.strip().upper()}`"
                    ),
                    discord.ui.Separator(visible=True),
                ]
            )

        container_items.extend(
            [
                discord.ui.TextDisplay(self.description),
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    f"-# Submitted by {self.submitter} | "
                    f"<t:{int(discord.utils.utcnow().timestamp())}:f>"
                ),
            ]
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

    async def update_review(
        self,
        world_name: str,
        description: str,
    ):
        self.world_name = world_name
        self.description = description

        self.build_view()

        if self.review_message:
            await self.review_message.edit(view=self)