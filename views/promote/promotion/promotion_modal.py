
import discord

from views.promote.promotion.review_view import PromotionReviewView
from services.emoji.emoji_parser import parse_emojis

class PromoteModal(discord.ui.Modal, title="Promote Item / World"):
    def __init__(
        self,
        review_view: PromotionReviewView | None = None,
    ):
        super().__init__()

        self.review_view = review_view

        self.world_name = discord.ui.TextInput(
            label="World Name",
            placeholder="Enter the world name (optional)",
            required=False,
            max_length=100,
            default=review_view.world_name if review_view else "",
        )

        self.description = discord.ui.TextInput(
            label="Description",
            placeholder="Describe the item, world, or service you want to promote...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
            default=review_view.description if review_view else "",
        )

        self.add_item(self.world_name)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        world_name = parse_emojis(self.world_name.value.strip())
        description = parse_emojis(self.description.value.strip())

        if self.review_view:
            await self.review_view.update_review(
                world_name=world_name,
                description=description,
            )
            await interaction.response.defer()
            return

        view = PromotionReviewView(
            world_name=world_name,
            description=description,
        )

        await interaction.response.send_message(
            view=view,
            ephemeral=True,
        )

        view.review_message = await interaction.original_response()
