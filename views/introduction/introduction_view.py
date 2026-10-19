import discord

from views.introduction.introduction_button import (
    IntroductionButton,
)


class IntroductionView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=None
        )

        self.add_item(
            IntroductionButton()
        )

    @staticmethod
    def get_embed() -> discord.Embed:

        return discord.Embed(
            title="Introduction Your GrowID",
            description=(
                "Please enter your GrowID according to your game information.\n"
                "-# Your Discord display name will be updated based on the GrowID you enter."
            ),
            color=discord.Color.from_str("#5865F2")
        )