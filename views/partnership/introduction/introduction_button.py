import discord

from database.main.user.intro_manager import (
    get_introduction
)

from views.partnership.introduction.introduction_modal import (
    IntroductionModal
)


class IntroductionButton(
    discord.ui.Button
):

    def __init__(self):
        super().__init__(
            label="Introduction",
            style=discord.ButtonStyle.primary,
            custom_id="growlink:introduction"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        user_id = interaction.user.id

        try:

            nickname, growid = await get_introduction(
                user_id=user_id
            )

            await interaction.response.send_modal(
                IntroductionModal(
                    nickname_value=nickname,
                    growid_value=growid
                )
            )

        except Exception as e:

            print(
                f"[Introduction] Failed to load "
                f"user {user_id}: {e}"
            )

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Terjadi kesalahan saat mengambil data Introduction.",
                    ephemeral=True
                )