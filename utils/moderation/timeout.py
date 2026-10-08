from datetime import timedelta

import discord

from utils.moderation.delete_scheduler import (
    register_delete,
)

from views.member.moderation.timeout_view import (
    TimeoutView,
)


async def timeout_member(
    member: discord.Member,
    duration: timedelta,
    reason: str | None = None,
) -> bool:

    try:

        await member.timeout(
            duration,
            reason=reason,
        )

    except (
        discord.Forbidden,
        discord.HTTPException,
    ):

        return False

    try:

        duration_minutes = int(
            duration.total_seconds() / 60
        )

        if duration_minutes < 60:

            duration_text = (
                f"{duration_minutes} minutes"
            )

        elif duration_minutes % 60 == 0:

            duration_text = (
                f"{duration_minutes // 60} hours"
            )

        else:

            duration_text = (
                f"{duration_minutes // 60} hours "
                f"{duration_minutes % 60} minutes"
            )

        embed = discord.Embed(
            title="⏱️ You have been timed out",
            description=(
                "You are temporarily unable to "
                "send messages, add reactions, "
                "or interact in the server."
            ),
        )

        embed.add_field(
            name="Server",
            value=f"`{member.guild.name}`",
            inline=False,
        )

        embed.add_field(
            name="Duration",
            value=f"`{duration_text}`",
            inline=True,
        )

        embed.add_field(
            name="Reason",
            value=(
                f"`{reason}`"
                if reason
                else "No reason provided."
            ),
            inline=False,
        )

        embed.set_footer(
            text=(
                "If you believe the timeout should be "
                "removed, you can use the button below."
            )
        )

        view = TimeoutView(
            guild_id=member.guild.id,
            member_id=member.id,
        )

        dm_message = await member.send(
            embed=embed,
            view=view,
        )

        delete_after = (
            duration + timedelta(hours=12)
        )

        await register_delete(
            channel_id=dm_message.channel.id,
            message_id=dm_message.id,
            delete_after=delete_after,
        )

    except (
        discord.Forbidden,
        discord.HTTPException,
    ):

        pass

    return True