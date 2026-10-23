
import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.loader import load_cogs
from core.presence import set_bot_presence
from core.sync import sync_commands

from database.database import (
    init_databases,
    close_databases,
)

from database.growlink.emoji_manager import reload_emojis
from events.guild.guild_join import handle_guild_join
from events.guild.guild_remove import handle_guild_remove
from events.member.member_join import handle_member_join
from events.message.message_create import handle_message_create

from services.bots.bot_guild_sync import sync_bot_guilds
from services.bots.guild_key_sync import sync_guild_keys
from services.bots.user_sync import (
    sync_all_members,
    sync_guild_members,
)

from services.phishing.review_restore import restore_phishing_review_views

from utils.moderation.delete_scheduler import delete_checker

from views.moderation.timeout_view import RemoveTimeoutButton
from views.introduction.introduction_view import IntroductionView
from views.promote.promote_view import PromoteView


# ======================
# ENVIRONMENT
# ======================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN tidak ditemukan. Periksa file .env."
    )


# ======================
# LOGGING
# ======================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

class DiscordReconnectFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not (
            record.name == "discord.gateway"
            and "has successfully RESUMED session" in record.getMessage()
        )


reconnect_filter = DiscordReconnectFilter()

logging.getLogger("discord.gateway").addFilter(
    reconnect_filter
)

for handler in logging.getLogger().handlers:
    handler.addFilter(reconnect_filter)

logging.getLogger("asyncmy").setLevel(logging.ERROR)
logging.getLogger("discord").setLevel(logging.INFO)

logger = logging.getLogger("growlink")

# ======================
# INTENTS
# ======================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# ======================
# BOT CLASS
# ======================

class GrowLink(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delete_task = None
        self._databases_initialized = False

    async def setup_hook(self):
        logger.info("Memulai setup GrowLink...")

        try:
            await init_databases()
            self._databases_initialized = True
            logger.info("Database berhasil diinisialisasi.")

            await load_cogs(self)
            logger.info("Cogs berhasil dimuat.")

            await sync_commands(self)
            logger.info("Sinkronisasi command selesai.")

            self.add_view(IntroductionView())
            self.add_view(PromoteView())
            self.add_dynamic_items(RemoveTimeoutButton)

            logger.info("Persistent views berhasil didaftarkan.")

            await restore_phishing_review_views(self)
            logger.info("Pemulihan phishing review selesai.")

        except Exception:
            logger.exception("Terjadi kesalahan saat setup GrowLink.")
            raise

    async def close(self):
        logger.info("Menutup GrowLink...")

        if self.delete_task is not None and not self.delete_task.done():
            self.delete_task.cancel()

            try:
                await self.delete_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("Kesalahan saat menghentikan delete checker.")

        if self._databases_initialized:
            try:
                await close_databases()
                logger.info("Koneksi database ditutup.")
            except Exception:
                logger.exception("Gagal menutup koneksi database.")

        await super().close()


# ======================
# CREATE BOT
# ======================

bot = GrowLink(
    command_prefix="!",
    intents=intents,
)

_ready_synced = False


# ======================
# READY EVENT
# ======================

@bot.event
async def on_ready():
    global _ready_synced

    logger.info("=" * 40)
    logger.info("GrowLink online sebagai: %s", bot.user)
    logger.info("Bot ID: %s", bot.user.id)
    logger.info("discord.py version: %s", discord.__version__)
    logger.info("=" * 40)

    try:
        await set_bot_presence(bot)
    except Exception:
        logger.exception("Gagal memperbarui presence bot.")

    # ======================
    # LOAD EMOJIS
    # ======================

    try:
        await reload_emojis()
        logger.info("Cache emoji berhasil dimuat ulang.")
    except Exception:
        logger.exception("Gagal memuat emoji dari database.")

    if _ready_synced:
        logger.info("Inisialisasi on_ready sudah dilakukan sebelumnya.")
        return

    _ready_synced = True

    try:
        await sync_bot_guilds(bot)
        await sync_guild_keys(bot)
        await sync_all_members(bot)

        logger.info("Sinkronisasi guild dan member selesai.")

    except Exception:
        logger.exception("Gagal saat sinkronisasi guild/member.")
        _ready_synced = False
        return

    if bot.delete_task is None or bot.delete_task.done():
        bot.delete_task = asyncio.create_task(
            delete_checker(bot),
            name="growlink-delete-checker",
        )
        logger.info("Delete checker dimulai.")

# ======================
# GUILD EVENTS
# ======================

@bot.event
async def on_guild_join(guild: discord.Guild):
    logger.info(
        "Bot bergabung ke guild: %s (%s)",
        guild.name,
        guild.id,
    )

    try:
        await handle_guild_join(bot, guild)
        await sync_guild_members(guild)
    except Exception:
        logger.exception(
            "Gagal memproses guild baru: %s (%s)",
            guild.name,
            guild.id,
        )


@bot.event
async def on_guild_remove(guild: discord.Guild):
    logger.info(
        "Bot keluar dari guild: %s (%s)",
        guild.name,
        guild.id,
    )

    try:
        await handle_guild_remove(bot, guild)
    except Exception:
        logger.exception(
            "Gagal memproses guild yang ditinggalkan: %s",
            guild.id,
        )


# ======================
# MEMBER EVENTS
# ======================

@bot.event
async def on_member_join(member: discord.Member):
    try:
        await handle_member_join(member)
    except Exception:
        logger.exception(
            "Gagal memproses member baru: %s (%s)",
            member,
            member.id,
        )


# ======================
# MESSAGE EVENT
# ======================

@bot.event
async def on_message(message: discord.Message):
    try:
        await handle_message_create(bot, message)
    except Exception:
        logger.exception(
            "Gagal memproses pesan %s",
            message.id,
        )

    await bot.process_commands(message)


# ======================
# PREFIX COMMAND ERROR
# ======================

@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError,
):
    if isinstance(error, commands.CommandNotFound):
        return

    logger.error(
        "Prefix command error pada %s",
        ctx.command,
        exc_info=(type(error), error, error.__traceback__),
    )


# ======================
# START BOT
# ======================

if __name__ == "__main__":
    logger.info("Menjalankan GrowLink...")

    bot.run(
        TOKEN,
        log_level=logging.INFO,
    )
