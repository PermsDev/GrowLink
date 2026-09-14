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
        label="Nama Panggilan",
        placeholder="Masukkan nama panggilan kamu...",
        required=True,
        max_length=32
    )

    growid = discord.ui.TextInput(
        label="GrowID Growtopia",
        placeholder="Masukkan GrowID Growtopia kamu...",
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

            # ======================
            # SAVE INTRODUCTION
            # ======================

            await save_introduction(
                user_id=user_id,
                nickname=nickname,
                growid=growid
            )

            # ======================
            # UPDATE DISPLAY NAME
            # ======================

            display_status = await update_member_display_name(
                member=interaction.user
            )

            # ======================
            # RESPONSE
            # ======================

            if display_status == "updated":
                display_message = (
                    "✅ Display name Discord berhasil diperbarui."
                )

            elif display_status == "already_same":
                display_message = (
                    "✅ Display name Discord sudah sesuai."
                )

            elif display_status == "role_too_low":
                display_message = (
                    "⚠️ Introduction berhasil disimpan, "
                    "tetapi display name Discord tidak dapat diubah "
                    "karena role bot lebih rendah atau sama dengan "
                    "role kamu."
                )

            elif display_status == "no_source":
                display_message = (
                    "⚠️ Introduction berhasil disimpan, "
                    "tetapi display source belum tersedia."
                )

            elif display_status == "no_data":
                display_message = (
                    "⚠️ Introduction berhasil disimpan, "
                    "tetapi data untuk display name tidak tersedia."
                )

            else:
                display_message = (
                    "⚠️ Introduction berhasil disimpan, "
                    "tetapi display name Discord tidak berubah."
                )


            await interaction.response.send_message(
                (
                    "✅ **Introduction berhasil disimpan!**\n\n"
                    f"**Nama Panggilan:** {nickname}\n"
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
                    "❌ Terjadi kesalahan saat menyimpan Introduction.",
                    ephemeral=True
                )
