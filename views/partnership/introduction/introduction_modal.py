import discord

from database.main.user.intro_manager import (
    save_introduction
)

from services.partnership.display_name.display_name_service import (
    update_member_display_name,
)


class IntroductionModal(
    discord.ui.Modal,
    title="Introduction"
):

    nickname = discord.ui.TextInput(
        label="Nickname",
        placeholder="Enter your nickname...",
        required=True,
        max_length=32
    )

    growid = discord.ui.TextInput(
        label="GrowID Growtopia",
        placeholder="Enter your GrowID...",
        required=True,
        max_length=32
    )

    def __init__(
        self,
        nickname_value: str | None = None,
        growid_value: str | None = None
    ):
        super().__init__()

        if nickname_value is not None:
            self.nickname.default = nickname_value

        if growid_value is not None:
            self.growid.default = growid_value

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        user_id = interaction.user.id

        nickname = self.nickname.value.strip()
        growid = self.growid.value.strip()

        try:

            await save_introduction(
                user_id=user_id,
                nickname=nickname,
                growid=growid
            )

            display_status = await update_member_display_name(
                member=interaction.user
            )

            if display_status == "updated":
                display_message = (
                    "✅ Your Discord display name has been updated."
                )

            elif display_status == "already_same":
                display_message = (
                    "✅ Your Discord display name is already up to date."
                )

            elif display_status == "role_too_low":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but your Discord display name could not be changed "
                    "because the bot's role is lower than or equal to "
                    "your role."
                )

            elif display_status == "no_source":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but the display source is not available."
                )

            elif display_status == "no_data":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but the data required for the display name "
                    "is not available."
                )

            else:
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but your Discord display name was not changed."
                )

            await interaction.response.send_message(
                (
                    "✅ **Introduction saved successfully!**\n\n"
                    f"**Nickname:** {nickname}\n"
                    f"**GrowID:** {growid}\n\n"
                    f"{display_message}"
                ),
                ephemeral=True
            )

        except Exception as e:

            print(
                f"[Introduction] Failed to save "
                f"user {user_id}: {e}"
            )

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while saving your Introduction.",
                    ephemeral=True
                )