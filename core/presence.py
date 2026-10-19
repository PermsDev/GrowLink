import discord


async def set_bot_presence(bot: discord.Client):
    await bot.change_presence(
        activity=discord.CustomActivity(
            name="Version 1.2.0"
        )
    )
