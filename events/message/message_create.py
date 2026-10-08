import aiohttp
import discord

from services.phishing.multi_image_detector import (
    analyze_multi_images,
)

from services.phishing.review_service import (
    send_phishing_review,
)


async def handle_message_create(
    bot: discord.Client,
    message: discord.Message,
):

    if message.author.bot:
        return

    if not message.attachments:
        return

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
        return

    images = []

    async with aiohttp.ClientSession() as session:

        for attachment in image_attachments:

            try:

                async with session.get(
                    attachment.url
                ) as response:

                    if response.status != 200:

                        print(
                            "[PHISHING] "
                            "Gagal download: "
                            f"{attachment.filename}"
                        )

                        continue

                    image_bytes = (
                        await response.read()
                    )

                    if image_bytes:

                        images.append(
                            (
                                attachment.filename,
                                image_bytes,
                            )
                        )

            except Exception as error:

                print(
                    "[PHISHING] "
                    "Error download "
                    f"{attachment.filename}: {error}"
                )

    if not images:
        return

    guild_id = (
        message.guild.id
        if message.guild
        else None
    )

    guild_name = (
        message.guild.name
        if message.guild
        else "Direct Message"
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

    image_bytes_list = [
        image_bytes
        for _, image_bytes
        in images
    ]

    result = await analyze_multi_images(
        images=image_bytes_list,
        discord_user_id=message.author.id,
        guild_id=guild_id,
        member=message.author,
        message=message,
    )

    status = result["status"]

    results = result["results"]

    total_images = result[
        "total_images"
    ]

    phishing_count = result[
        "phishing_count"
    ]

    print()
    print("=" * 50)
    print("PHISHING IMAGE DETECTION")
    print("=" * 50)

    print(
        f"Server        : {guild_name}"
    )

    print(
        f"Guild ID      : {guild_id}"
    )

    print(
        f"Channel       : #{channel_name}"
    )

    print(
        f"Channel ID    : {channel_id}"
    )

    print(
        f"User          : {message.author}"
    )

    print(
        f"User ID       : {message.author.id}"
    )

    print(
        f"Images        : {total_images}"
    )

    print(
        f"Phishing      : {phishing_count}"
    )

    print(
        "Threshold     : 80.00%"
    )

    print(
        f"Overall Status : {status.upper()}"
    )

    print("-" * 50)

    for index, detection in enumerate(
        results,
        start=1,
    ):

        print(
            f"[IMAGE {index}] "
            f"Similarity: "
            f"{detection.similarity:.2f}% | "
            f"Matched ID: "
            f"{detection.matched_image_id} | "
            f"Phishing: "
            f"{detection.is_phishing}"
        )

    print("=" * 50)
    print()

    if status == "review":

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

    return result