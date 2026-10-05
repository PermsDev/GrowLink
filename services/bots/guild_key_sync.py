import discord

from database.main.guilds.guild_key_manager import (
    get_guild_key,
    add_guild_key,
    get_general_guild_ids,
    remove_guild_key,
)


async def sync_guild_keys(
    bot: discord.Client
):
    """
    Sinkronisasi guild_key dengan guild yang
    sedang dimiliki bot.

    Rules:
        - Guild bot yang belum memiliki key
          -> General
        - General yang guild-nya sudah tidak dimiliki bot
          -> dihapus
        - Partnership tidak pernah dihapus oleh sync ini
    """
    
    # print(f"[SYNC GUILD KEYS] {bot.user.name} ({bot.user.id})")

    # ==================================================
    # GET GUILDS YANG DIMILIKI BOT
    # ==================================================
    bot_guild_ids = {
        guild.id
        for guild in bot.guilds
    }

    # ==================================================
    # ADD GENERAL UNTUK GUILD TANPA KEY
    # ==================================================
    for guild in bot.guilds:

        guild_key = await get_guild_key(
            guild_id=guild.id
        )

        if guild_key is not None:
            continue

        await add_guild_key(
            guild_id=guild.id
        )

    # ==================================================
    # REMOVE GENERAL YANG SUDAH TIDAK DIMILIKI BOT
    # ==================================================
    general_guild_ids = await get_general_guild_ids()

    for guild_id in general_guild_ids:

        if guild_id in bot_guild_ids:
            continue

        await remove_guild_key(
            guild_id=guild_id
        )