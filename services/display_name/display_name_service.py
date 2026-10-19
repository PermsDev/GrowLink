import discord

from config.constants import FEATURE_INTRODUCTION

from database.main.user.intro_manager import (
    get_introduction,
)

from database.growlink.feature_manager import (
    get_active_feature_guild_ids,
)


async def update_member_display_name(
    bot: discord.Client,
    user_id: int,
) -> dict:
    introduction = await get_introduction(
        user_id=user_id
    )

    if not introduction:
        return {
            "status": "no_data",
            "guilds": {},
        }

    _, growid = introduction

    if not growid:
        return {
            "status": "no_data",
            "guilds": {},
        }

    guild_ids = await get_active_feature_guild_ids(
        feature_type=FEATURE_INTRODUCTION
    )

    if not guild_ids:
        return {
            "status": "no_active_guild",
            "guilds": {},
        }

    results = {}

    for guild_id in guild_ids:
        guild = bot.get_guild(guild_id)

        if guild is None:
            results[guild_id] = "bot_not_in_guild"
            continue

        member = guild.get_member(user_id)

        if member is None:
            try:
                member = await guild.fetch_member(user_id)
            except discord.NotFound:
                results[guild_id] = "not_in_guild"
                continue
            except discord.Forbidden:
                results[guild_id] = "member_fetch_forbidden"
                continue
            except discord.HTTPException:
                results[guild_id] = "fetch_failed"
                continue

        if member.bot:
            results[guild_id] = "bot_member"
            continue

        if member.nick == growid:
            results[guild_id] = "already_same"
            continue

        bot_member = guild.me

        if bot_member is None:
            results[guild_id] = "role_too_low"
            continue

        if member.top_role >= bot_member.top_role:
            results[guild_id] = "role_too_low"
            continue

        try:
            await member.edit(
                nick=growid,
                reason="GrowLink Introduction display name",
            )
        except discord.Forbidden:
            results[guild_id] = "update_forbidden"
        except discord.HTTPException:
            results[guild_id] = "update_failed"
        else:
            results[guild_id] = "updated"

    if "updated" in results.values():
        status = "updated"
    elif "already_same" in results.values():
        status = "already_same"
    elif results and all(
        value == "not_in_guild"
        for value in results.values()
    ):
        status = "not_in_guild"
    else:
        status = "completed"

    return {
        "status": status,
        "guilds": results,
    }