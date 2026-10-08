import hashlib
from io import BytesIO

import aiohttp
import imagehash
from PIL import Image


def calculate_sha256(
    image_bytes: bytes,
) -> str:
    return hashlib.sha256(
        image_bytes
    ).hexdigest()


def calculate_phash(
    image_bytes: bytes,
) -> str:
    image = Image.open(
        BytesIO(image_bytes)
    )

    image = image.convert("RGB")

    return str(
        imagehash.phash(image)
    )


def calculate_similarity(
    source_phash: str,
    target_phash: str,
) -> float:
    source = imagehash.hex_to_hash(
        source_phash
    )

    target = imagehash.hex_to_hash(
        target_phash
    )

    distance = source - target

    total_bits = len(
        source.hash
    ) ** 2

    similarity = (
        1
        - (
            distance
            / total_bits
        )
    ) * 100

    return max(
        0.0,
        min(
            100.0,
            similarity,
        ),
    )


async def download_image(
    url: str,
) -> bytes:
    timeout = aiohttp.ClientTimeout(
        total=30
    )

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(
            url
        ) as response:

            response.raise_for_status()

            return await response.read()


async def check_phishing_image(
    image_bytes: bytes,
    discord_user_id: int | None = None,
    guild_id: int | None = None,
):
    from database.growlink.phishing.phishing_image_manager import (
        get_active_images,
        get_by_sha256,
    )

    sha256 = calculate_sha256(
        image_bytes
    )

    existing = await get_by_sha256(
        sha256
    )

    if existing:

        return {
            "is_phishing": True,
            "similarity": 100.0,
            "matched_image_id": existing[0],
            "sha256": sha256,
            "phash": existing[2],
            "created": False,
            "reason": "exact_match",
        }

    phash = calculate_phash(
        image_bytes
    )

    phishing_images = (
        await get_active_images()
    )

    best_similarity = 0.0
    matched_image_id = None

    for image in phishing_images:

        image_id = image[0]
        stored_phash = image[2]

        similarity = calculate_similarity(
            phash,
            stored_phash,
        )

        if similarity > best_similarity:

            best_similarity = similarity
            matched_image_id = image_id

    return {
        "is_phishing": (
            best_similarity >= 80.0
        ),
        "similarity": best_similarity,
        "matched_image_id": matched_image_id,
        "sha256": sha256,
        "phash": phash,
        "created": False,
        "reason": (
            "similar_match"
            if best_similarity >= 80.0
            else "below_threshold"
        ),
    }


async def check_phishing_image_url(
    image_url: str,
    discord_user_id: int | None = None,
    guild_id: int | None = None,
):
    image_bytes = await download_image(
        image_url
    )

    return await check_phishing_image(
        image_bytes=image_bytes,
        discord_user_id=discord_user_id,
        guild_id=guild_id,
    )