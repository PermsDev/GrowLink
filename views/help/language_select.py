
import discord

class LanguageSelect(discord.ui.Select):
    LANGUAGE_LABELS = {
        "en": ("English", "🇬🇧"),
        "id": ("Bahasa Indonesia", "🇮🇩"),
    }

    def __init__(self, help_view):
        self.help_view = help_view

        translations = help_view.help_data.get("translations", {})

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
                    default=language == help_view.language,
                )
            )

        super().__init__(
            placeholder="🌐 Select language / Pilih bahasa",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="growlink:help:language",
        )

    async def callback(self, interaction: discord.Interaction):
        self.help_view.language = self.values[0]
        self.help_view._build()

        await interaction.response.edit_message(
            view=self.help_view
        )
