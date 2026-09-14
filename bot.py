import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.loader import load_cogs
from core.sync import sync_commands

from database.database import (
    init_databases,
    close_databases,
)
from events.guild.guild_join import handle_guild_join
from events.guild.guild_remove import handle_guild_remove
from events.member.member_join import handle_member_join
from services.bots.bot_guild_sync import sync_bot_guilds
from services.bots.guild_key_sync import sync_guild_keys
from services.bots.user_sync import sync_all_members, sync_guild_members
from views.partnership.introduction.introduction_view import IntroductionView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class GrowLink(commands.Bot):

    async def setup_hook(self):
        await init_databases()
        await load_cogs(self)
        await sync_commands(self)
        self.add_view( IntroductionView() )

    async def close(self):
        await close_databases()
        await super().close()


bot = GrowLink(
    command_prefix="!",
    intents=intents
)

_ready_synced = False


@bot.event
async def on_ready():

    global _ready_synced

    print("=" * 40)
    print(f"GrowLink online sebagai: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 40)

    if _ready_synced:
        return

    _ready_synced = True

    await sync_bot_guilds(bot)
    await sync_guild_keys(bot)
    await sync_all_members(bot)

# ======================
# GUILD EVENTS
# ======================
@bot.event
async def on_guild_join(guild):
    await handle_guild_join(bot, guild)
    await sync_guild_members(guild)

@bot.event
async def on_guild_remove(guild):
    await handle_guild_remove(bot, guild)

@bot.event
async def on_member_join(member):
    await handle_member_join(member)


# ======================
# ERROR HANDLER (!)
# ======================
@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError
):

    if isinstance(error, commands.CommandNotFound):
        return
    raise error

bot.run(TOKEN)