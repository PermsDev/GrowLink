
import math

import discord

from database.growlink.emoji_manager import (
    get_emojis,
    get_emoji,
)
from utils.locale_loader import get_translations
from views.components.language_select import LanguageSelect


EMOJIS_PER_PAGE = 20


class PreviousPageButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(
            emoji="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=view.page <= 0,
            custom_id="growlink:promote:emoji_list:previous",
        )
        self.emoji_view = view

    async def callback(self, interaction: discord.Interaction):
        self.emoji_view.page -= 1
        self.emoji_view._build()

        await interaction.response.edit_message(
            view=self.emoji_view
        )


class PageIndicatorButton(discord.ui.Button):
    def __init__(self, page: int, total_pages: int):
        super().__init__(
            label=f"{page + 1}/{total_pages}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            custom_id="growlink:promote:emoji_list:page",
        )


class NextPageButton(discord.ui.Button):
    def __init__(self, view, total_pages: int):
        super().__init__(
            emoji="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=view.page >= total_pages - 1,
            custom_id="growlink:promote:emoji_list:next",
        )
        self.emoji_view = view

    async def callback(self, interaction: discord.Interaction):
        self.emoji_view.page += 1
        self.emoji_view._build()

        await interaction.response.edit_message(
            view=self.emoji_view
        )


class EmojiListView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=180)

        self.translations = get_translations(
            "emoji/emoji_list.json"
        )
        self.language = self._get_default_language()
        self.page = 0

        self._build()

    def _get_default_language(self):
        if "en" in self.translations:
            return "en"

        if self.translations:
            return next(iter(self.translations))

        return "en"

    async def on_language_select(
        self,
        interaction: discord.Interaction,
        language: str,
    ):
        if language not in self.translations:
            await interaction.response.defer()
            return

        self.language = language
        self._build()

        await interaction.response.edit_message(
            view=self
        )

    def _build(self):
        self.clear_items()

        texts = self.translations.get(
            self.language,
            self.translations.get("en", {}),
        )

        emojis = sorted(get_emojis())
        total_pages = max(
            1,
            math.ceil(len(emojis) / EMOJIS_PER_PAGE),
        )

        self.page = max(
            0,
            min(self.page, total_pages - 1),
        )

        start_index = self.page * EMOJIS_PER_PAGE
        end_index = start_index + EMOJIS_PER_PAGE
        page_emojis = emojis[start_index:end_index]

        container_items = [
            discord.ui.TextDisplay(
                f"## {texts.get('title', '🧩 GrowLink Emoji List')}"
            ),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(
                f"**{texts.get('instructions_title', 'How to use')}**\n"
                f"{texts.get('instructions', '')}"
            ),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(
                f"**{texts.get('available', 'Available Emojis')}**"
            ),
        ]

        if page_emojis:
            emoji_lines = [
                f"{start_index + index + 1}. "
                f"{get_emoji(key, default=f':{key}:')} `:{key}:`"
                for index, key in enumerate(page_emojis)
            ]

            container_items.append(
                discord.ui.TextDisplay(
                    "\n".join(emoji_lines)
                )
            )
        else:
            container_items.append(
                discord.ui.TextDisplay(
                    texts.get(
                        "empty",
                        "No emojis are currently available.",
                    )
                )
            )

        container_items.extend(
            [
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    texts.get(
                        "footer",
                        "-# Emoji list is loaded from the current cache.",
                    )
                ),
            ]
        )

        self.add_item(
            discord.ui.Container(
                *container_items,
                accent_colour=discord.Color.green(),
            )
        )

        if self.translations:
            self.add_item(
                discord.ui.ActionRow(
                    LanguageSelect(
                        translations=self.translations,
                        current_language=self.language,
                        callback_handler=self.on_language_select,
                        custom_id="growlink:promote:emoji_list:language",
                    )
                )
            )
        
        self.add_item(
            discord.ui.ActionRow(
                PreviousPageButton(self),
                PageIndicatorButton(
                    self.page,
                    total_pages,
                ),
                NextPageButton(
                    self,
                    total_pages,
                ),
            )
        )



class EmojiListButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Emoji List",
            emoji="🧩",
            style=discord.ButtonStyle.secondary,
            custom_id="growlink:promote:emoji_list",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=EmojiListView(),
            ephemeral=True,
        )
