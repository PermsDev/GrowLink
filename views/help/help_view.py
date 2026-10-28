
import discord

from views.help.commands import COMMAND_HELP
from database.growlink.emoji_manager import get_emoji
from views.components.language_select import LanguageSelect


class HelpView(discord.ui.LayoutView):
    LABELS = {
        "title": f"{get_emoji('digi')} GrowLink Help",
        "details": "Description",
        "options": "Options",
        "usage": "Usage",
        "permissions": "Permissions",
        "examples": "Examples",
        "required": "Required",
        "optional": "Optional",
        "undocumented": "Documentation Unavailable",
        "undocumented_details": (
            "Documentation for this command "
            "is not available yet."
        ),
        "footer": "GrowLink • Help Center",
    }

    def __init__(self, command: str):
        super().__init__(timeout=180)

        self.command = command
        self.help_data = COMMAND_HELP.get(command)
        self.language = self._get_default_language()

        self._build()

    def _get_default_language(self):
        if self.help_data is None:
            return "en"

        translations = self.help_data.get("translations", {})

        if "en" in translations:
            return "en"

        if translations:
            return next(iter(translations))

        return "en"

    def get_text(self, key, default=None):
        if self.help_data is None:
            return default

        translations = self.help_data.get("translations", {})
        language_data = translations.get(self.language, {})
        english_data = translations.get("en", {})

        return language_data.get(
            key,
            english_data.get(key, default),
        )

    async def on_language_select(
        self,
        interaction: discord.Interaction,
        language: str,
    ):
        self.language = language
        self._build()

        await interaction.response.edit_message(
            view=self
        )

    def _build(self):
        self.clear_items()

        labels = self.LABELS
        container = discord.ui.Container()

        container.add_item(
            discord.ui.TextDisplay(
                f"# {labels['title']}"
            )
        )

        container.add_item(
            discord.ui.Separator()
        )

        if self.help_data is None:
            container.add_item(
                discord.ui.TextDisplay(
                    f"## {labels['undocumented']}\n"
                    f"Command: `/{self.command}`\n\n"
                    f"{labels['undocumented_details']}"
                )
            )
        else:
            name = self.help_data.get("name", self.command)
            description = self.get_text("description", "")
            details = self.get_text("details", "")
            options = self.get_text("options", [])
            usage = self.get_text("usage", [])
            permissions = self.get_text("permissions", [])
            examples = self.get_text("examples", [])

            container.add_item(
                discord.ui.TextDisplay(
                    f"## `/{name}`\n{description}"
                )
            )

            if details and details.strip():
                container.add_item(
                    discord.ui.Separator()
                )

                container.add_item(
                    discord.ui.TextDisplay(
                        f"### {labels['details']}\n"
                        f"{details.strip()}"
                    )
                )

            if options:
                options_text = "\n\n".join(
                    f"**`{option['name']}`** "
                    f"({labels['required'] if option.get('required', False) else labels['optional']})\n"
                    f"{option.get('description', '')}"
                    for option in options
                )

                container.add_item(
                    discord.ui.Separator()
                )

                container.add_item(
                    discord.ui.TextDisplay(
                        f"### {labels['options']}\n"
                        f"{options_text}"
                    )
                )

            if usage:
                usage_text = "\n".join(
                    f"- {item}"
                    for item in usage
                )

                container.add_item(
                    discord.ui.Separator()
                )

                container.add_item(
                    discord.ui.TextDisplay(
                        f"### {labels['usage']}\n"
                        f"{usage_text}"
                    )
                )

            if permissions:
                permissions_text = "\n".join(
                    f"- {permission}"
                    for permission in permissions
                )

                container.add_item(
                    discord.ui.Separator()
                )

                container.add_item(
                    discord.ui.TextDisplay(
                        f"### {labels['permissions']}\n"
                        f"{permissions_text}"
                    )
                )

            if examples:
                examples_text = "\n\n".join(
                    f"**{example['command']}**\n"
                    f"{example.get('description', '')}"
                    for example in examples
                )

                container.add_item(
                    discord.ui.Separator()
                )

                container.add_item(
                    discord.ui.TextDisplay(
                        f"### {labels['examples']}\n"
                        f"{examples_text}"
                    )
                )

        container.add_item(
            discord.ui.Separator()
        )

        container.add_item(
            discord.ui.TextDisplay(
                f"-# {labels['footer']}"
            )
        )

        self.add_item(container)

        if self.help_data is not None:
            translations = self.help_data.get("translations", {})

            if translations:
                self.add_item(
                    discord.ui.ActionRow(
                        LanguageSelect(
                            translations=translations,
                            current_language=self.language,
                            callback_handler=self.on_language_select,
                            custom_id="growlink:help:language",
                        )
                    )
                )
