import discord


async def delete_message(
    message: discord.Message,
    reason: str | None = None,
) -> bool:

    try:

        await message.delete()

        print(
            "[Moderation] Message deleted "
            f"| Message ID: {message.id}"
        )

        return True

    except discord.NotFound:

        print(
            "[Moderation] Message already deleted "
            f"| Message ID: {message.id}"
        )

        return True

    except discord.Forbidden:

        print(
            "[Moderation] Failed to delete message: "
            "Missing permissions "
            f"| Message ID: {message.id}"
        )

        return False

    except discord.HTTPException as e:

        print(
            "[Moderation] Failed to delete message: "
            f"{e} "
            f"| Message ID: {message.id}"
        )

        return False