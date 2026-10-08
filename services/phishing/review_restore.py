import discord

from database.growlink.phishing.phishing_review_manager import (
    get_review_actions_for_restore,
    get_reviews_by_action_id,
)

from views.member.phishing.phishing_review_view import (
    PhishingReviewView,
)


async def restore_phishing_review_views(
    bot: discord.Client,
):
    actions = await get_review_actions_for_restore()

    restored = 0

    for action in actions:

        action_id = action[0]
        review_message_id = action[3]

        reviews = await get_reviews_by_action_id(
            action_id
        )

        if not reviews:
            continue

        review_ids = []

        result_map = {}

        for index, review in enumerate(
            reviews,
            start=1,
        ):

            review_id = review[0]

            review_ids.append(
                review_id
            )

            result_map[review_id] = {
                "index": index,
                "similarity": float(
                    review[4]
                ),
                "matched_image_id": review[5],
                "status": review[6],
                "action": action[8],
            }

        view = PhishingReviewView(
            review_ids=review_ids,
            result_map=result_map,
        )

        bot.add_view(
            view,
            message_id=review_message_id,
        )

        restored += 1

    print(
        f"Phishing review views restored: {restored}"
    )