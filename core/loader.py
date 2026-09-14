import os
from discord.ext import commands


async def load_cogs(bot: commands.Bot):
    print("[Loader] Loading Cogs...")

    for root, _, files in os.walk("cogs"):
        for file in files:
            if not file.endswith(".py"):
                continue

            if file.startswith("_"):
                continue

            path = os.path.join(root, file)

            extension = path[:-3].replace(os.sep, ".")

            try:
                await bot.load_extension(extension)
                print(f"[Loader] Loaded: {extension}")

            except Exception as e:
                print(f"[Loader] Failed: {extension}")
                print(f"[Loader] Error: {e}")