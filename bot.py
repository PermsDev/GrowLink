import asyncio
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
from events.message.message_create import handle_message_create

from services.bots.bot_guild_sync import sync_bot_guilds
from services.bots.guild_key_sync import sync_guild_keys
from services.bots.user_sync import sync_all_members, sync_guild_members
from services.phishing.review_restore import restore_phishing_review_views
from utils.moderation.delete_scheduler import delete_checker
from views.member.moderation.timeout_view import RemoveTimeoutButton
from views.partnership.introduction.introduction_view import IntroductionView

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

import logging

logging.getLogger("asyncmy").setLevel(logging.ERROR)

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class GrowLink(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delete_task = None

    async def setup_hook(self):
        await init_databases()
        await load_cogs(self)
        await sync_commands(self)
        
        self.add_view(IntroductionView())
        self.add_dynamic_items(
            RemoveTimeoutButton
        )
        await restore_phishing_review_views(self)

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
    # DELETE CHECKER
    # ======================
    if (
        bot.delete_task is None
        or bot.delete_task.done()
    ):
        bot.delete_task = asyncio.create_task(
            delete_checker(bot)
        )

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

@bot.event
async def on_message(message):

    await handle_message_create(bot, message)
    await bot.process_commands(message)

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