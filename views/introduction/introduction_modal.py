import discord

from database.main.user.intro_manager import (
    get_introduction,
    save_introduction,
)

from services.display_name.display_name_service import (
    update_member_display_name,
)

from views.introduction.introduction_role_service import (
    give_introduction_role,
)

from services.api.permacore_api import (
    update_growid_card,
)


class IntroductionModal(
    discord.ui.Modal,
    title="Introduction",
):

    nickname = discord.ui.TextInput(
        label="Nickname",
        placeholder="Enter your nickname...",
        required=True,
        max_length=32,
    )

    growid = discord.ui.TextInput(
        label="GrowID Growtopia",
        placeholder="Enter your GrowID...",
        required=True,
        max_length=32,
    )

    def __init__(
        self,
        nickname_value: str | None = None,
        growid_value: str | None = None,
    ):
        super().__init__()

        if nickname_value is not None:
            self.nickname.default = nickname_value

        if growid_value is not None:
            self.growid.default = growid_value

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(
            ephemeral=True,
            thinking=True,
        )

        user_id = interaction.user.id

        nickname = self.nickname.value.strip()
        growid = self.growid.value.strip()

        try:
            old_nickname, old_growid = await get_introduction(
                user_id=user_id,
            )

            profile_exists = old_nickname is not None

            profile_changed = (
                old_nickname != nickname
                or old_growid != growid
            )

            await save_introduction(
                user_id=user_id,
                nickname=nickname,
                growid=growid,
            )

            if isinstance(interaction.user, discord.Member):
                try:
                    await give_introduction_role(
                        member=interaction.user,
                    )
                except Exception as error:
                    print(
                        "[Introduction] Failed to assign "
                        f"GT_intro role for user {user_id} "
                        f"in guild {interaction.guild_id}: {error}"
                    )

            permacore_status = None

            if profile_exists and profile_changed:
                permacore_status = await update_growid_card(
                    user_id=user_id,
                )

            display_result = await update_member_display_name(
                bot=interaction.client,
                user_id=user_id,
            )

            display_status = display_result["status"]
            guild_results = display_result.get("guilds", {})

            if display_status == "updated":
                display_message = (
                    "✅ Your Discord display name has been updated "
                    "in at least one eligible server."
                )

            elif display_status == "already_same":
                display_message = (
                    "✅ Your Discord display name is already up to date."
                )

            elif display_status == "no_data":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but your GrowID is unavailable."
                )

            elif display_status == "no_active_guild":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but no server has the Introduction feature enabled."
                )

            elif display_status == "not_in_guild":
                display_message = (
                    "⚠️ Your Introduction was saved, "
                    "but you were not found in any eligible server."
                )

            else:
                updated_count = sum(
                    status == "updated"
                    for status in guild_results.values()
                )

                failed_count = sum(
                    status in {
                        "bot_not_in_guild",
                        "member_fetch_forbidden",
                        "fetch_failed",
                        "role_too_low",
                        "update_forbidden",
                        "update_failed",
                    }
                    for status in guild_results.values()
                )

                display_message = (
                    "⚠️ Your Introduction was saved.\n"
                    f"Servers updated: {updated_count}\n"
                    f"Servers requiring attention: {failed_count}"
                )

            if permacore_status is False:
                display_message += (
                    "\n⚠️ Your Introduction was saved, but the "
                    "GrowID card update in PermaCore failed."
                )

            await interaction.followup.send(
                (
                    "✅ **Introduction saved successfully!**\n\n"
                    f"**Nickname:** {nickname}\n"
                    f"**GrowID:** {growid}\n\n"
                    f"{display_message}"
                ),
                ephemeral=True,
            )

        except Exception as error:
            print(
                "[Introduction] Failed to process "
                f"user {user_id}: {error}"
            )

            error_message = (
                "❌ An error occurred while processing your Introduction."
            )

            try:
                await interaction.followup.send(
                    error_message,
                    ephemeral=True,
                )
            except discord.HTTPException as response_error:
                print(
                    "[Introduction] Failed to send error response "
                    f"for user {user_id}: {response_error}"
                )
