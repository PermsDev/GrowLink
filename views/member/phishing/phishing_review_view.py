from datetime import timedelta

import discord

from database.growlink.phishing.phishing_image_manager import (
    add_phishing_image,
    get_by_sha256,
)

from database.growlink.phishing.phishing_review_manager import (
    get_review_by_id,
    update_review_status,
    get_report_action_by_review_id,
    update_review_action_to_punished,
)

from utils.moderation.delete_message import (
    delete_message,
)

from utils.moderation.timeout import (
    timeout_member,
)


class PhishingReviewView(
    discord.ui.View
):
    def __init__(
        self,
        review_ids: list[int],
        result_map: dict[int, dict],
    ):
        super().__init__(
            timeout=None
        )

        self.review_ids = review_ids
        self.result_map = result_map

        self.selected_review_id = None

        self.processed_review_ids = {
            review_id
            for review_id, data
            in result_map.items()
            if data.get("status") in (
                "approved",
                "rejected",
            )
        }

        self.action_status = "reported"

        for data in result_map.values():

            if data.get("action") == "punished":

                self.action_status = "punished"

                break

        all_processed = (
            len(self.processed_review_ids)
            >= len(self.review_ids)
        )

        self.select = discord.ui.Select(
            placeholder=(
                "Select an image to review"
            ),
            options=[
                discord.SelectOption(
                    label=(
                        f"Image {data['index']}"
                    ),
                    description=(
                        f"Similarity "
                        f"{data['similarity']:.2f}%"
                    ),
                    value=str(review_id),
                )
                for review_id, data
                in result_map.items()
            ][:25],
            custom_id=(
                "phishing_review:select:"
                f"{review_ids[0]}"
            ),
            disabled=all_processed,
        )

        self.select.callback = (
            self.select_callback
        )

        self.approve_button = discord.ui.Button(
            label="Approve",
            style=discord.ButtonStyle.success,
            custom_id=(
                "phishing_review:approve:"
                f"{review_ids[0]}"
            ),
            disabled=True,
        )

        self.reject_button = discord.ui.Button(
            label="Reject",
            style=discord.ButtonStyle.danger,
            custom_id=(
                "phishing_review:reject:"
                f"{review_ids[0]}"
            ),
            disabled=True,
        )

        self.punishment_button = discord.ui.Button(
            label="Give Punishment",
            style=discord.ButtonStyle.primary,
            custom_id=(
                "phishing_review:punishment:"
                f"{review_ids[0]}"
            ),
            disabled=(
                not all_processed
                or self.action_status == "punished"
            ),
        )

        self.approve_button.callback = (
            self.approve_callback
        )

        self.reject_button.callback = (
            self.reject_callback
        )

        self.punishment_button.callback = (
            self.punishment_callback
        )

        self.add_item(
            self.select
        )

        self.add_item(
            self.approve_button
        )

        self.add_item(
            self.reject_button
        )

        self.add_item(
            self.punishment_button
        )

    async def get_report_data(
        self,
        review_id: int,
    ):

        review = await get_review_by_id(
            review_id
        )

        if not review:
            return None

        action = await get_report_action_by_review_id(
            review_id
        )

        if not action:
            return None

        return {
            "action_id": action[0],
            "guild_id": action[1],
            "message_id": action[2],
            "review_message_id": action[3],
            "channel_id": action[4],
            "reported_user_id": action[5],
            "reporter_user_id": action[6],
            "reviewer_user_id": action[7],
            "action": action[8],
        }

    async def select_callback(
        self,
        interaction: discord.Interaction,
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            review_id = int(
                self.select.values[0]
            )

            review = await get_review_by_id(
                review_id
            )

            if not review:

                await interaction.followup.send(
                    "Review not found.",
                    ephemeral=True,
                )

                return

            status = review[6]

            data = self.result_map.get(
                review_id
            )

            if not data:

                await interaction.followup.send(
                    "Image data could not be found.",
                    ephemeral=True,
                )

                return

            self.selected_review_id = (
                review_id
            )

            if status != "pending":

                self.approve_button.disabled = True
                self.reject_button.disabled = True

                await interaction.followup.send(
                    (
                        f"**Image {data['index']} selected**\n\n"
                        f"Status: "
                        f"`{status.upper()}`\n"
                        f"Similarity: "
                        f"`{data['similarity']:.2f}%`\n"
                        f"Matched ID: "
                        f"`{data['matched_image_id']}`"
                    ),
                    ephemeral=True,
                )

                if interaction.message:

                    await interaction.message.edit(
                        view=self
                    )

                return

            self.approve_button.disabled = False
            self.reject_button.disabled = False

            matched_id = data[
                "matched_image_id"
            ]

            matched_text = (
                str(matched_id)
                if matched_id is not None
                else "None"
            )

            await interaction.followup.send(
                (
                    f"**Image {data['index']} selected**\n\n"
                    f"Status: `PENDING`\n"
                    f"Similarity: "
                    f"`{data['similarity']:.2f}%`\n"
                    f"Matched ID: "
                    f"`{matched_text}`\n\n"
                    f"Please select "
                    f"**Approve** or **Reject**."
                ),
                ephemeral=True,
            )

            if interaction.message:

                await interaction.message.edit(
                    view=self
                )

        except Exception as error:

            print(
                "[PHISHING REVIEW] "
                f"Select callback error: {error}"
            )

            try:

                await interaction.followup.send(
                    (
                        "An error occurred while "
                        "processing the selected image."
                    ),
                    ephemeral=True,
                )

            except (
                discord.HTTPException,
                discord.NotFound,
            ):

                pass

    async def approve_callback(
        self,
        interaction: discord.Interaction,
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        if self.selected_review_id is None:

            await interaction.followup.send(
                (
                    "Please select an image "
                    "from the dropdown first."
                ),
                ephemeral=True,
            )

            return

        review_id = (
            self.selected_review_id
        )

        review = await get_review_by_id(
            review_id
        )

        if not review:

            await interaction.followup.send(
                "Review not found.",
                ephemeral=True,
            )

            return

        if review[6] != "pending":

            await interaction.followup.send(
                (
                    f"This review has already "
                    f"been marked as "
                    f"`{review[6].upper()}`."
                ),
                ephemeral=True,
            )

            return

        report_data = await self.get_report_data(
            review_id
        )

        if not report_data:

            await interaction.followup.send(
                "Report information could not be found.",
                ephemeral=True,
            )

            return

        existing = await get_by_sha256(
            review[2]
        )

        if not existing:

            await add_phishing_image(
                sha256=review[2],
                phash=review[3],
                discord_user_id=(
                    report_data[
                        "reported_user_id"
                    ]
                ),
                guild_id=(
                    report_data[
                        "guild_id"
                    ]
                ),
                source="discord",
            )

        status_updated = (
            await update_review_status(
                review_id=review_id,
                status="approved",
            )
        )

        if not status_updated:

            await interaction.followup.send(
                "Failed to update the review status.",
                ephemeral=True,
            )

            return

        self.result_map[
            review_id
        ]["status"] = "approved"

        self.processed_review_ids.add(
            review_id
        )

        self.selected_review_id = None

        self.approve_button.disabled = True
        self.reject_button.disabled = True

        all_processed = (
            len(self.processed_review_ids)
            >= len(self.review_ids)
        )

        self.select.disabled = (
            all_processed
        )

        self.punishment_button.disabled = (
            not all_processed
            or self.action_status == "punished"
        )

        image_index = self.result_map[
            review_id
        ]["index"]

        await interaction.followup.send(
            (
                f"Image `{image_index}` "
                f"has been approved.\n"
                f"Status: `APPROVED`\n"
                f"The image has been added "
                f"to `phishing_image`."
            ),
            ephemeral=True,
        )

        if interaction.message:

            await interaction.message.edit(
                view=self
            )

    async def reject_callback(
        self,
        interaction: discord.Interaction,
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        if self.selected_review_id is None:

            await interaction.followup.send(
                (
                    "Please select an image "
                    "from the dropdown first."
                ),
                ephemeral=True,
            )

            return

        review_id = (
            self.selected_review_id
        )

        review = await get_review_by_id(
            review_id
        )

        if not review:

            await interaction.followup.send(
                "Review not found.",
                ephemeral=True,
            )

            return

        if review[6] != "pending":

            await interaction.followup.send(
                (
                    f"This review has already "
                    f"been marked as "
                    f"`{review[6].upper()}`."
                ),
                ephemeral=True,
            )

            return

        report_data = await self.get_report_data(
            review_id
        )

        if not report_data:

            await interaction.followup.send(
                "Report information could not be found.",
                ephemeral=True,
            )

            return

        status_updated = (
            await update_review_status(
                review_id=review_id,
                status="rejected",
            )
        )

        if not status_updated:

            await interaction.followup.send(
                "Failed to update the review status.",
                ephemeral=True,
            )

            return

        self.result_map[
            review_id
        ]["status"] = "rejected"

        self.processed_review_ids.add(
            review_id
        )

        self.selected_review_id = None

        self.approve_button.disabled = True
        self.reject_button.disabled = True

        all_processed = (
            len(self.processed_review_ids)
            >= len(self.review_ids)
        )

        self.select.disabled = (
            all_processed
        )

        self.punishment_button.disabled = (
            not all_processed
            or self.action_status == "punished"
        )

        image_index = self.result_map[
            review_id
        ]["index"]

        await interaction.followup.send(
            (
                f"Image `{image_index}` "
                f"has been rejected.\n"
                f"Status: `REJECTED`"
            ),
            ephemeral=True,
        )

        if interaction.message:

            await interaction.message.edit(
                view=self
            )

    async def punishment_callback(
        self,
        interaction: discord.Interaction,
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            review_id = self.review_ids[0]

            report_data = await self.get_report_data(
                review_id
            )

            if not report_data:

                await interaction.followup.send(
                    "Report information could not be found.",
                    ephemeral=True,
                )

                return

            if report_data["action"] == "punished":

                self.action_status = "punished"
                self.punishment_button.disabled = True

                await interaction.followup.send(
                    "This report has already been punished.",
                    ephemeral=True,
                )

                if interaction.message:

                    await interaction.message.edit(
                        view=self
                    )

                return

            all_processed = (
                len(self.processed_review_ids)
                >= len(self.review_ids)
            )

            if not all_processed:

                await interaction.followup.send(
                    (
                        "All images must be "
                        "reviewed before punishment "
                        "can be issued."
                    ),
                    ephemeral=True,
                )

                return

            action_id = report_data[
                "action_id"
            ]

            guild_id = report_data[
                "guild_id"
            ]

            message_id = report_data[
                "message_id"
            ]

            channel_id = report_data[
                "channel_id"
            ]

            reported_user_id = report_data[
                "reported_user_id"
            ]

            if guild_id is None:

                await interaction.followup.send(
                    "The server information could not be found.",
                    ephemeral=True,
                )

                return

            if reported_user_id is None:

                await interaction.followup.send(
                    "The reported user could not be found.",
                    ephemeral=True,
                )

                return

            guild = interaction.client.get_guild(
                guild_id
            )

            if guild is None:

                await interaction.followup.send(
                    "The server could not be found.",
                    ephemeral=True,
                )

                return

            target_member = guild.get_member(
                reported_user_id
            )

            if target_member is None:

                try:

                    target_member = (
                        await guild.fetch_member(
                            reported_user_id
                        )
                    )

                except (
                    discord.NotFound,
                    discord.HTTPException,
                ):

                    await interaction.followup.send(
                        "The reported user could not be found.",
                        ephemeral=True,
                    )

                    return

            message_deleted = False

            channel = guild.get_channel(
                channel_id
            )

            if channel is not None:

                try:

                    message = (
                        await channel.fetch_message(
                            message_id
                        )
                    )

                    message_deleted = (
                        await delete_message(
                            message=message,
                            reason=(
                                "Phishing punishment "
                                "issued by reviewer."
                            ),
                        )
                    )

                except (
                    discord.NotFound,
                    discord.HTTPException,
                ):

                    message_deleted = True

            timeout_success = (
                await timeout_member(
                    member=target_member,
                    duration=timedelta(
                        minutes=5
                    ),
                    reason=(
                        "Phishing punishment "
                        "issued by reviewer."
                    ),
                )
            )

            action_updated = (
                await update_review_action_to_punished(
                    action_id=action_id,
                    reviewer_user_id=(
                        interaction.user.id
                    ),
                )
            )

            if not action_updated:

                await interaction.followup.send(
                    "Failed to update the report action.",
                    ephemeral=True,
                )

                return

            self.action_status = "punished"
            self.punishment_button.disabled = True

            await interaction.followup.send(
                (
                    "Punishment has been issued.\n\n"
                    f"• Message deleted: "
                    f"{'Yes' if message_deleted else 'No'}\n"
                    f"• User timed out for 5 minutes: "
                    f"{'Yes' if timeout_success else 'No'}\n"
                    f"• Reviewer: "
                    f"`{interaction.user.id}`"
                ),
                ephemeral=True,
            )

            if interaction.message:

                await interaction.message.edit(
                    view=self
                )

        except Exception as error:

            print(
                "[PHISHING REVIEW] "
                f"Punishment callback error: {error}"
            )

            try:

                await interaction.followup.send(
                    (
                        "An error occurred while "
                        "issuing the punishment."
                    ),
                    ephemeral=True,
                )

            except (
                discord.HTTPException,
                discord.NotFound,
            ):

                pass