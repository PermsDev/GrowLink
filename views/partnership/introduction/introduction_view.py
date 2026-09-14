import discord

from views.partnership.introduction.introduction_button import (
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
            title="Introduction Your Growid",
            description=(
                "Silakan Mengisi Growid sesuai dengan data game kalian.\n"
                "-# Display Name akan berubah sesuai dengan Growid yang kalian masukkan."
            )
        )