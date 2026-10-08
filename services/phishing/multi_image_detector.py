from dataclasses import dataclass
from datetime import timedelta

import discord

from database.growlink.phishing.phishing_image_manager import (
    add_phishing_image,
    get_active_images,
    get_by_sha256,
)

from database.growlink.phishing.phishing_review_manager import (
    add_phishing_review,
    add_review_action,
)

from services.phishing.image_detector import (
    calculate_phash,
    calculate_sha256,
    calculate_similarity,
)

from utils.moderation.delete_message import (
    delete_message,
)

from utils.moderation.timeout import (
    timeout_member,
)


PHISHING_THRESHOLD = 80.0


@dataclass
class ImageDetectionResult:
    sha256: str
    phash: str
    similarity: float
    matched_image_id: int | None
    existing_image_id: int | None
    is_phishing: bool


async def analyze_image(
    image_bytes: bytes,
    phishing_images=None,
) -> ImageDetectionResult:

    sha256 = calculate_sha256(
        image_bytes
    )

    exact_match = await get_by_sha256(
        sha256
    )

    if exact_match:

        return ImageDetectionResult(
            sha256=sha256,
            phash=exact_match[2],
            similarity=100.0,
            matched_image_id=exact_match[0],
            existing_image_id=exact_match[0],
            is_phishing=True,
        )

    phash = calculate_phash(
        image_bytes
    )

    if phishing_images is None:

        phishing_images = (
            await get_active_images()
        )

    best_similarity = 0.0
    best_image_id = None

    for image in phishing_images:

        image_id = image[0]
        stored_phash = image[2]

        similarity = calculate_similarity(
            phash,
            stored_phash,
        )

        if similarity > best_similarity:

            best_similarity = similarity
            best_image_id = image_id

    return ImageDetectionResult(
        sha256=sha256,
        phash=phash,
        similarity=best_similarity,
        matched_image_id=best_image_id,
        existing_image_id=None,
        is_phishing=(
            best_similarity
            >= PHISHING_THRESHOLD
        ),
    )


async def analyze_multi_images(
    images: list[bytes],
    discord_user_id: int | None = None,
    guild_id: int | None = None,
    member: discord.Member | None = None,
    message: discord.Message | None = None,
):

    timeout_success = False
    delete_success = False
    review_ids = []

    if not images:

        return {
            "status": "safe",
            "results": [],
            "total_images": 0,
            "phishing_count": 0,
            "review_ids": [],
            "timeout": False,
            "delete": False,
        }

    phishing_images = (
        await get_active_images()
    )

    results = []

    for image_bytes in images:

        result = await analyze_image(
            image_bytes=image_bytes,
            phishing_images=phishing_images,
        )

        results.append(
            result
        )

    total_images = len(results)

    phishing_count = sum(
        1
        for result in results
        if result.is_phishing
    )

    if phishing_count == 0:

        status = "safe"

    elif phishing_count == total_images:

        status = "phishing"

    else:

        status = "review"

    if status == "phishing":

        inserted_sha256 = set()

        for result in results:

            if result.existing_image_id is not None:
                continue

            if result.sha256 in inserted_sha256:
                continue

            await add_phishing_image(
                sha256=result.sha256,
                phash=result.phash,
                discord_user_id=discord_user_id,
                guild_id=guild_id,
                source="discord",
            )

            inserted_sha256.add(
                result.sha256
            )

        if member is not None:

            timeout_success = (
                await timeout_member(
                    member=member,
                    duration=timedelta(
                        days=7
                    ),
                    reason="Phishing detected",
                )
            )

        if message is not None:

            delete_success = (
                await delete_message(
                    message=message,
                    reason="Phishing detected",
                )
            )

    elif status == "review":

        if message is not None:

            action_id = await add_review_action(
                guild_id=guild_id,
                message_id=message.id,
                channel_id=message.channel.id,
                reported_user_id=discord_user_id,
                reporter_user_id=None,
                reviewer_user_id=None,
                action="reported",
            )

            for result in results:

                review_id = (
                    await add_phishing_review(
                        phishing_review_action_id=action_id,
                        sha256=result.sha256,
                        phash=result.phash,
                        similarity=result.similarity,
                        matched_image_id=(
                            result.matched_image_id
                        ),
                    )
                )

                review_ids.append(
                    review_id
                )

    return {
        "status": status,
        "results": results,
        "total_images": total_images,
        "phishing_count": phishing_count,
        "review_ids": review_ids,
        "timeout": timeout_success,
        "delete": delete_success,
    }