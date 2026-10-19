
import discord

from views.promote.promote_buttons import (
    PromoteButton,
    PromoteInformationButton,
)


class PromotionWebhookView(discord.ui.LayoutView):
    def __init__(
        self,
        world_name: str,
        description: str,
        bot_name: str,
        submitter: discord.abc.User,
    ):
        super().__init__(timeout=None)

        container_items = [
            discord.ui.TextDisplay(
                "## <a:megaphone:1561145155937902712> GrowLink Promotion"
            ),
            discord.ui.Separator(visible=True),
        ]

        if world_name and world_name.strip():
            container_items.extend(
                [
                    discord.ui.TextDisplay(
                        f"**World Name:** {world_name.strip()}"
                    ),
                    discord.ui.Separator(visible=True),
                ]
            )

        container_items.extend(
            [
                discord.ui.TextDisplay(f"\n\n{description}"),
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    f"-# Submitted via {bot_name} by {submitter}"
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
