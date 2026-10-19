
import discord

from views.promote.promote_buttons import (
    PromoteButton,
    PromoteInformationButton,
)


class PromoteView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(
                    "## <:digi:1561217043376906421> GrowLink Promote\n"
                    "Promote your Growtopia items, worlds, or services "
                    "across Discord servers that have GrowLink Promote enabled."
                ),
                accent_colour=discord.Color.green(),
            )
        )

        self.add_item(
            discord.ui.ActionRow(
                PromoteButton(),
                PromoteInformationButton(),
            )
        )
