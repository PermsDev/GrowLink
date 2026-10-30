import discord
from discord import app_commands
from discord.ext import commands

from views.emoji.emoji_view import EmojiListView


class EmojiList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="emoji-list",
        description="Display the available GrowLink emojis.",
    )
    async def emoji_list(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.send_message(
            view=EmojiListView(),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(EmojiList(bot))