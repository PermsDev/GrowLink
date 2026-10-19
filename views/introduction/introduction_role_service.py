import discord

from database.growlink.role_manager import get_role


ROLE_KEY = "GT_intro"


async def give_introduction_role(
    member: discord.Member,
) -> str:
    role_id = await get_role(
        guild_id=member.guild.id,
        role_key=ROLE_KEY,
    )

    if role_id is None:
        return "role_not_configured"

    role = member.guild.get_role(role_id)

    if role is None:
        return "role_not_found"

    if role in member.roles:
        return "already_has_role"

    try:
        await member.add_roles(
            role,
            reason="Completed GrowLink Introduction",
        )
        return "added"

    except discord.Forbidden:
        return "forbidden"

    except discord.HTTPException:
        return "failed"