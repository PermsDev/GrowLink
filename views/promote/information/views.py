
import discord

from database.growlink.emoji_manager import get_emoji

class PromoteInformationView:
    @staticmethod
    async def send(interaction: discord.Interaction):
        await interaction.response.send_message(
            f"## {get_emoji('guide')} About GrowLink Promote\n"
            "GrowLink Promote allows you to promote Growtopia items, "
            "worlds, or services you offer across Discord servers "
            "that have this feature enabled.\n\n"
            "**How it works:**\n"
            "1. Click **Promote Item / World** to get started.\n"
            "2. Provide the requested promotion details.\n"
            "3. Your promotion can be distributed to servers "
            "that have GrowLink Promote enabled.\n\n"
            f"-# {get_emoji('warning')} Promotion submission and distribution are currently in beta testing.",
            ephemeral=True,
        )
