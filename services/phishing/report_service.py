from datetime import timedelta

import aiohttp
import discord

from database.growlink.phishing.phishing_image_manager import (
    get_active_images,
)

from database.growlink.phishing.phishing_review_manager import (
    add_phishing_review,
    add_review_action,
    get_report_action_by_message_id,
)

from services.phishing.multi_image_detector import (
    analyze_image,
)

from services.phishing.review_service import (
    send_phishing_review,
)

from utils.moderation.delete_message import (
    delete_message,
)

from utils.moderation.timeout import (
    timeout_member,
)


def is_staff_or_moderator(
    member: discord.Member,
) -> bool:

    permissions = member.guild_permissions

    return (
        permissions.administrator
        or permissions.manage_messages
        or permissions.moderate_members
    )


async def download_report_images(
    message: discord.Message,
):

    image_attachments = [
        attachment
        for attachment in message.attachments
        if (
            attachment.content_type
            and attachment.content_type.startswith(
                "image/"
            )
        )
    ]

    if not image_attachments:
        return []

    images = []

    async with aiohttp.ClientSession() as session:

        for attachment in image_attachments:

            try:

                async with session.get(
                    attachment.url
                ) as response:

                    if response.status != 200:

                        print(
                            "[PHISHING REPORT] "
                            "Failed to download: "
                            f"{attachment.filename}"
                        )

                        continue

                    image_bytes = await response.read()

                    if image_bytes:

                        images.append(
                            (
                                attachment.filename,
                                image_bytes,
                            )
                        )

            except Exception as error:

                print(
                    "[PHISHING REPORT] "
                    "Download error "
                    f"{attachment.filename}: "
                    f"{error}"
                )

    return images


async def create_report_reviews(
    message: discord.Message,
    images: list[tuple[str, bytes]],
    reporter_user_id: int | None = None,
):

    phishing_images = await get_active_images()

    results = []
    review_ids = []

    guild_id = (
        message.guild.id
        if message.guild is not None
        else None
    )

    reported_user_id = message.author.id

    action_id = await add_review_action(
        message_id=message.id,
        channel_id=message.channel.id,
        action="reported",
        guild_id=guild_id,
        reported_user_id=reported_user_id,
        reporter_user_id=reporter_user_id,
        reviewer_user_id=None,
    )

    for _, image_bytes in images:

        result = await analyze_image(
            image_bytes=image_bytes,
            phishing_images=phishing_images,
        )

        results.append(result)

        review_id = await add_phishing_review(
            phishing_review_action_id=action_id,
            sha256=result.sha256,
            phash=result.phash,
            similarity=result.similarity,
            matched_image_id=result.matched_image_id,
        )

        review_ids.append(review_id)

    return {
        "status": "review",
        "results": results,
        "total_images": len(results),
        "phishing_count": sum(
            1
            for result in results
            if result.is_phishing
        ),
        "review_ids": review_ids,
        "action_id": action_id,
    }


async def report_message(
    bot: discord.Client,
    interaction: discord.Interaction,
    message: discord.Message,
):

    if message.author.bot:

        await interaction.response.send_message(
            "You cannot report a bot message.",
            ephemeral=True,
        )

        return

    await interaction.response.defer(
        ephemeral=True
    )

    reporter_user_id = interaction.user.id

    existing_report = (
        await get_report_action_by_message_id(
            message.id
        )
    )

    if existing_report:

        await interaction.followup.send(
            (
                "This message has already "
                "been reported and is currently "
                "under review."
            ),
            ephemeral=True,
        )

        return

    images = await download_report_images(
        message
    )

    if not images:

        await interaction.followup.send(
            (
                "The reported message does not "
                "contain any images."
            ),
            ephemeral=True,
        )

        return

    result = await create_report_reviews(
        message=message,
        images=images,
        reporter_user_id=reporter_user_id,
    )

    guild_name = (
        message.guild.name
        if message.guild is not None
        else "Direct Message"
    )

    guild_id = (
        message.guild.id
        if message.guild is not None
        else None
    )

    channel_name = (
        message.channel.name
        if hasattr(
            message.channel,
            "name",
        )
        else "Unknown"
    )

    channel_id = message.channel.id

    await send_phishing_review(
        bot=bot,
        message=message,
        result=result,
        images=images,
        guild_name=guild_name,
        guild_id=guild_id,
        channel_name=channel_name,
        channel_id=channel_id,
    )

    reporter_is_staff = False

    if (
        interaction.guild is not None
        and isinstance(
            interaction.user,
            discord.Member,
        )
    ):

        reporter_is_staff = (
            is_staff_or_moderator(
                interaction.user
            )
        )

    deleted = False
    timed_out = False

    if reporter_is_staff:

        print(
            "[PHISHING REPORT] "
            "Reporter is staff/moderator "
            f"| Reporter ID: "
            f"{reporter_user_id}"
        )

        deleted = await delete_message(
            message=message,
            reason=(
                "Phishing message reported "
                "by staff/moderator."
            ),
        )

        if (
            message.guild is not None
            and isinstance(
                message.author,
                discord.Member,
            )
        ):

            timed_out = await timeout_member(
                member=message.author,
                duration=timedelta(
                    minutes=5
                ),
                reason=(
                    "Phishing message reported "
                    "by staff/moderator."
                ),
            )

        print(
            "[PHISHING REPORT] "
            "Moderation result "
            f"| Deleted: {deleted} "
            f"| Timed out: {timed_out} "
            f"| Target ID: "
            f"{message.author.id}"
        )

    else:

        print(
            "[PHISHING REPORT] "
            "Reporter is not staff/moderator "
            f"| Reporter ID: "
            f"{reporter_user_id}"
        )

    await interaction.followup.send(
        (
            "The message has been reported "
            "and sent to the developer for review."
        ),
        ephemeral=True,
    )