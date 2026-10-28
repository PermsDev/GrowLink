import discord


class LanguageSelect(discord.ui.Select):
    LANGUAGE_LABELS = {
        "en": ("English", "🇬🇧"),
        "id": ("Bahasa Indonesia", "🇮🇩"),
    }

    def __init__(
        self,
        translations: dict,
        current_language: str,
        callback_handler,
        custom_id: str = "growlink:language:select",
    ):
        self.translations = translations
        self.callback_handler = callback_handler

        options = []

        for language in translations:
            label, emoji = self.LANGUAGE_LABELS.get(
                language,
                (language.upper(), "🌐"),
            )

            options.append(
                discord.SelectOption(
                    label=label,
                    value=language,
                    emoji=emoji,
                    default=language == current_language,
                )
            )

        super().__init__(
            placeholder="🌐 Select language / Pilih bahasa",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=custom_id,
        )

    async def callback(self, interaction: discord.Interaction):
        await self.callback_handler(
            interaction,
            self.values[0],
        )