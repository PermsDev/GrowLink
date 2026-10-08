import os
from io import BytesIO

import discord

from database.growlink.phishing.phishing_review_manager import (
    update_review_message_id,
)

from views.member.phishing.phishing_review_view import (
    PhishingReviewView,
)


REVIEW_CHANNEL_ID = int(
    os.getenv(
        "PHISHING_REVIEW_CHANNEL_ID",
        "0",
    )
)


async def send_phishing_review(
    bot: discord.Client,
    message: discord.Message,
    result: dict,
    images: list[tuple[str, bytes]],
    guild_name: str,
    guild_id: int | None,
    channel_name: str,
    channel_id: int,
):

    if not REVIEW_CHANNEL_ID:

        print(
            "[PHISHING REVIEW] "
            "PHISHING_REVIEW_CHANNEL_ID "
            "belum dikonfigurasi."
        )

        return

    channel = bot.get_channel(
        REVIEW_CHANNEL_ID
    )

    if channel is None:

        try:

            channel = await bot.fetch_channel(
                REVIEW_CHANNEL_ID
            )

        except Exception as error:

            print(
                "[PHISHING REVIEW] "
                f"Gagal mengambil channel: {error}"
            )

            return

    if not isinstance(
        channel,
        discord.TextChannel,
    ):

        print(
            "[PHISHING REVIEW] "
            "Channel bukan TextChannel."
        )

        return

    action_id = result["action_id"]
    results = result["results"]
    review_ids = result["review_ids"]

    result_map = {}

    for index, (
        review_id,
        detection,
    ) in enumerate(
        zip(
            review_ids,
            results,
        ),
        start=1,
    ):

        result_map[review_id] = {
            "index": index,
            "similarity": (
                detection.similarity
            ),
            "matched_image_id": (
                detection.matched_image_id
            ),
            "status": "pending",
            "action": "reported",
        }

    embed = discord.Embed(
        title="🔍 Phishing Image Review",
        description=(
            "Pilih gambar dari dropdown "
            "untuk menentukan status gambar."
        ),
    )

    embed.add_field(
        name="Server",
        value=(
            f"**{guild_name}**\n"
            f"`{guild_id}`"
        ),
        inline=False,
    )

    embed.add_field(
        name="Channel",
        value=(
            f"#{channel_name}\n"
            f"`{channel_id}`"
        ),
        inline=True,
    )

    embed.add_field(
        name="User",
        value=(
            f"{message.author.mention}\n"
            f"`{message.author.id}`"
        ),
        inline=True,
    )

    embed.add_field(
        name="Message ID",
        value=f"`{message.id}`",
        inline=True,
    )

    embed.add_field(
        name="Total Images",
        value=str(
            result["total_images"]
        ),
        inline=True,
    )

    embed.add_field(
        name="Phishing Images",
        value=str(
            result["phishing_count"]
        ),
        inline=True,
    )

    details = []

    for index, detection in enumerate(
        results,
        start=1,
    ):

        matched_id = (
            detection.matched_image_id
        )

        matched_text = (
            str(matched_id)
            if matched_id is not None
            else "Tidak ada"
        )

        details.append(
            f"**Image {index}**\n"
            f"Similarity: "
            f"`{detection.similarity:.2f}%`\n"
            f"Matched ID: "
            f"`{matched_text}`"
        )

    embed.add_field(
        name="Detection Results",
        value="\n\n".join(details),
        inline=False,
    )

    files = []

    for index, (
        filename,
        image_bytes,
    ) in enumerate(
        images,
        start=1,
    ):

        extension = (
            filename.rsplit(
                ".",
                1,
            )[-1]
        )

        upload_name = (
            f"review_{message.id}_"
            f"{index}.{extension}"
        )

        files.append(
            discord.File(
                BytesIO(image_bytes),
                filename=upload_name,
            )
        )

    view = PhishingReviewView(
        review_ids=review_ids,
        result_map=result_map,
    )

    review_message = await channel.send(
        embed=embed,
        files=files,
        view=view,
    )

    updated = await update_review_message_id(
        action_id=action_id,
        review_message_id=review_message.id,
    )

    if not updated:

        print(
            "[PHISHING REVIEW] "
            "Gagal menyimpan review_message_id "
            f"(Action ID: {action_id})"
        )

        return

    print(
        "[PHISHING REVIEW] "
        "Review dikirim ke channel developer "
        f"(Server: {guild_name} | "
        f"Guild ID: {guild_id} | "
        f"Message ID: {message.id} | "
        f"Review Message ID: {review_message.id} | "
        f"Action ID: {action_id})"
    )