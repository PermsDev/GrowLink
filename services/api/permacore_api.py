import os

import aiohttp


async def update_growid_card(
    user_id: int,
) -> bool:
    api_url = os.getenv(
        "PERMACORE_INTERNAL_API_URL",
        "http://permacore-api:8765/internal/update-growid-card",
    )

    api_token = os.getenv(
        "INTERNAL_API_TOKEN",
        "",
    ).strip()

    if not api_token:
        print(
            "[PermaCore API] INTERNAL_API_TOKEN is missing."
        )
        return False

    try:
        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(
            timeout=timeout,
        ) as session:
            async with session.post(
                api_url,
                json={
                    "user_id": user_id,
                },
                headers={
                    "Authorization": f"Bearer {api_token}",
                },
            ) as response:

                result = await response.json(
                    content_type=None,
                )

                if response.status != 200:
                    print(
                        "[PermaCore API] Request failed "
                        f"with HTTP {response.status}: {result}"
                    )
                    return False

                if not isinstance(result, dict):
                    print(
                        "[PermaCore API] Invalid API response."
                    )
                    return False

                if not result.get("success"):
                    print(
                        "[PermaCore API] Failed to update "
                        f"GrowID card: {result}"
                    )
                    return False

                print(
                    "[PermaCore API] GrowID card updated "
                    f"for user {user_id}."
                )

                return True

    except Exception as error:
        print(
            "[PermaCore API] Request failed "
            f"for user {user_id}: {error}"
        )
        return False
