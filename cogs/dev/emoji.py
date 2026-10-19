
import re

import discord
from discord.ext import commands

from database.growlink.emoji_manager import set_emoji
from utils.moderation.delete_scheduler import register_delete
from config.settings import OWNER_ID


EMOJI_PATTERN = re.compile(
    r"<(?P<animated>a?):(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>"
)

class AddEmojiModal(discord.ui.Modal, title="Tambah Emoji"):
    emojis = discord.ui.TextInput(
        label="Emoji Discord",
        placeholder="Tempel satu emoji per baris",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    def __init__(self, view: "AddEmojiView"):
        super().__init__()
        self.view_ref = view

    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(
                "Sedang menyimpan emoji...",
                ephemeral=True,
            )
        except discord.NotFound:
            print(
                "[Emoji] Interaction kedaluwarsa sebelum respons. "
                f"Umur interaction: "
                f"{(discord.utils.utcnow() - interaction.created_at).total_seconds():.2f}s"
            )
            return

        lines = self.emojis.value.splitlines()

        added = 0
        invalid = []
        failed = []

        for line_number, line in enumerate(lines, start=1):
            line = line.strip()

            if not line:
                continue

            match = EMOJI_PATTERN.fullmatch(line)

            if not match:
                invalid.append(line_number)
                continue

            try:
                await set_emoji(
                    emoji_key=match.group("name"),
                    emoji_id=int(match.group("id")),
                    animated=bool(match.group("animated")),
                )
                added += 1

            except Exception:
                failed.append(line_number)

        result = [
            f"Berhasil menyimpan atau memperbarui: **{added} emoji**."
        ]

        if invalid:
            result.append(
                "Format tidak valid pada baris: "
                + ", ".join(map(str, invalid[:20]))
            )

        if failed:
            result.append(
                "Gagal menyimpan pada baris: "
                + ", ".join(map(str, failed[:20]))
            )

        await interaction.edit_original_response(
            content="\n".join(result)
        )

        await self.view_ref.delete_messages()


class AddEmojiView(discord.ui.View):
    def __init__(self, command_message: discord.Message):
        super().__init__(timeout=120)
        self.command_message = command_message
        self.panel_message = None

    async def delete_messages(self):
        for message in (self.command_message, self.panel_message):
            if message is None:
                continue

            try:
                await message.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

        self.stop()

    @discord.ui.button(
        label="Tambah Emoji",
        emoji="➕",
        style=discord.ButtonStyle.success,
        custom_id="growlink:add_emoji:open",
    )
    async def add_emoji(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "Hanya owner bot yang dapat menambahkan emoji.",
                ephemeral=True,
            )
            return
        
        await interaction.response.send_modal(AddEmojiModal(self))


class EmojiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="add", invoke_without_command=True)
    async def add(self, ctx: commands.Context):
        if ctx.author.id != OWNER_ID:
            return

        await ctx.send(
            "Gunakan `!add emoji` untuk menambahkan emoji."
        )

    @add.command(name="emoji")
    async def add_emoji(self, ctx: commands.Context):
        if ctx.author.id != OWNER_ID:
            return

        view = AddEmojiView(ctx.message)
        view.panel_message = await ctx.send(
            "Klik tombol di bawah untuk memasukkan emoji Discord.",
            view=view,
        )

        for message in (ctx.message, view.panel_message):
            await register_delete(
                channel_id=message.channel.id,
                message_id=message.id,
                delete_after="1h",
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiCog(bot))
