import discord


async def sync_commands(
    bot: discord.Client,
    guild: discord.Guild | None = None
):
    if guild:
        synced = await bot.tree.sync(guild=guild)
        print(
            f"[Sync] Guild -> {guild.name} "
            f"({len(synced)} Commands)"
        )
    else:
        synced = await bot.tree.sync()
        print(f"[Sync] Global -> ({len(synced)} Commands)")