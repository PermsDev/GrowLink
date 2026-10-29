import discord

from database.growlink.emoji_manager import get_emoji
from views.promote.promote_buttons import (
    PromoteButton,
    PromoteInformationButton,
)


class PromotionWebhookView(discord.ui.LayoutView):
    def __init__(
        self,
        world_name: str,
        description: str,
        submitter: discord.abc.User,
        bot_name: str = "GrowLink",
    ):
        super().__init__(timeout=None)

        container_items = [
            discord.ui.TextDisplay(
                f"## {get_emoji('digi')} GrowLink Promotion"
            ),
            discord.ui.Separator(visible=True),
        ]


        container_items.append(
            discord.ui.TextDisplay(description)
        )

        if world_name and world_name.strip():
            container_items.append(
                discord.ui.TextDisplay(
                    f"\n\n\n**World AT {get_emoji('bluearrow')}** `{world_name.strip()}`"
                )
            )

        container_items.extend(
            [
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    f"-# Submitted by {submitter} | "
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
                PromoteButton(),
                PromoteInformationButton(),
            )
        )
