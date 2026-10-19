
import logging

import discord

from config.constants import FEATURE_PROMOTION, PROMOTE_CHANNEL_KEY
from database.growlink.feature_manager import get_active_feature_guild_ids, deactivate_feature
from database.growlink.setup_manager import get_channel_id
from database.growlink.webhook_manager import ensure_channel_webhook
from database.main.game_manager import get_game_value
from views.promote.promotion.result_view import PromotionResultView

logger = logging.getLogger(__name__)


class SubmitPromotionButton(discord.ui.Button):
    def __init__(self, promotion_view: discord.ui.LayoutView):
        super().__init__(
            label="Submit Promotion",
            emoji="📨",
            style=discord.ButtonStyle.success,
            custom_id="growlink:promote:submit",
        )

        self.promotion_view = promotion_view

    async def callback(self, interaction: discord.Interaction):
        view = self.promotion_view

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Promotions can only be submitted from a server.",
                ephemeral=True,
            )
            return

        self.disabled = True
        await interaction.response.edit_message(view=view)

        sent_count = 0

        try:
            from views.promote.promotion.webhook.webhook_view import (
                PromotionWebhookView,
            )

            growid = await get_game_value(
                user_id=interaction.user.id,
                game_key="growtopia",
            )

            bot = interaction.client
            bot_user = bot.user
            submitter = interaction.user

            guild_ids = await get_active_feature_guild_ids(
                FEATURE_PROMOTION
            )

            for guild_id in guild_ids:
                try:
                    channel_id = await get_channel_id(
                        guild_id=guild_id,
                        channel_key=PROMOTE_CHANNEL_KEY,
                    )

                    if channel_id is None:
                        logger.warning(
                            "Promotion channel is not configured "
                            "for guild %s",
                            guild_id,
                        )
                        continue

                    channel_id = int(channel_id)

                    guild = bot.get_guild(guild_id)

                    if guild is None:
                        logger.warning(
                            "Guild %s is not available in bot cache",
                            guild_id,
                        )
                        continue

                    channel = guild.get_channel(channel_id)

                    if channel is None:
                        try:
                            channel = await bot.fetch_channel(channel_id)

                        except discord.NotFound:
                            logger.warning(
                                "Promotion channel %s was deleted. "
                                "Disabling promotion feature for guild %s.",
                                channel_id,
                                guild_id,
                            )

                            await deactivate_feature(
                                guild_id=guild_id,
                                feature_type=FEATURE_PROMOTION,
                            )
                            continue

                        except discord.Forbidden:
                            logger.warning(
                                "No permission to access promotion channel %s "
                                "in guild %s. Feature remains active.",
                                channel_id,
                                guild_id,
                            )
                            continue

                        except discord.HTTPException:
                            logger.exception(
                                "Failed to fetch promotion channel %s "
                                "in guild %s. Feature remains active.",
                                channel_id,
                                guild_id,
                            )
                            continue

                    if not isinstance(channel, discord.TextChannel):
                        logger.warning(
                            "Promotion channel %s is not a text channel. "
                            "Feature remains active.",
                            channel_id,
                        )
                        continue

                    if channel.guild.id != guild_id:
                        logger.warning(
                            "Channel %s does not belong to guild %s",
                            channel_id,
                            guild_id,
                        )
                        continue

                    webhook = await ensure_channel_webhook(
                        bot=bot,
                        channel=channel,
                    )

                    webhook_view = PromotionWebhookView(
                        world_name=view.world_name,
                        description=view.description,
                        bot_name=(
                            bot_user.name if bot_user else "GrowLink"
                        ),
                        submitter=submitter,
                    )

                    await webhook.send(
                        view=webhook_view,
                        username=growid or "GrowLink",
                        avatar_url=submitter.display_avatar.url,
                        allowed_mentions=discord.AllowedMentions.none(),
                    )

                    sent_count += 1

                    logger.info(
                        "Promotion sent successfully to guild %s, "
                        "channel %s",
                        guild_id,
                        channel_id,
                    )

                except discord.HTTPException:
                    logger.exception(
                        "Discord HTTP error sending promotion to guild %s",
                        guild_id,
                    )
                    continue
                except (ValueError, TypeError):
                    logger.exception(
                        "Invalid promotion configuration for guild %s",
                        guild_id,
                    )
                    continue
                except Exception:
                    logger.exception(
                        "Unexpected error sending promotion to guild %s",
                        guild_id,
                    )
                    continue

        except Exception:
            logger.exception("Failed to process promotion submission")

        await interaction.edit_original_response(
            view=PromotionResultView(success=sent_count > 0)
        )


class EditPromotionButton(discord.ui.Button):
    def __init__(self, promotion_view: discord.ui.LayoutView):
        super().__init__(
            label="Edit",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id="growlink:promote:edit",
        )

        self.promotion_view = promotion_view

    async def callback(self, interaction: discord.Interaction):
        from views.promote.promotion.promotion_modal import PromoteModal

        await interaction.response.send_modal(
            PromoteModal(review_view=self.promotion_view)
        )
