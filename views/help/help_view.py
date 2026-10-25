
import discord

from views.help.commands import COMMAND_HELP


class HelpView(discord.ui.LayoutView):
    def __init__(self, command: str):
        super().__init__(timeout=180)

        self.command = command
        self.container = discord.ui.Container()

        self._build()

        self.add_item(self.container)

    def _build(self):
        help_data = COMMAND_HELP.get(self.command)

        self.container.add_item(
            discord.ui.TextDisplay(
                "# GrowLink Help"
            )
        )

        self.container.add_item(
            discord.ui.Separator()
        )

        if help_data is None:
            self.container.add_item(
                discord.ui.TextDisplay(
                    "## Command belum memiliki dokumentasi\n"
                    f"Command: `/{self.command}`\n\n"
                    "Dokumentasi untuk command ini belum tersedia."
                )
            )

            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    "-# GrowLink • Help Center"
                )
            )
            return

        self.container.add_item(
            discord.ui.TextDisplay(
                f"## `/{help_data.NAME}`\n"
                f"{help_data.DESCRIPTION}"
            )
        )

        if getattr(help_data, "DETAILS", None):
            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    f"### Penjelasan\n{help_data.DETAILS.strip()}"
                )
            )

        options = getattr(help_data, "OPTIONS", [])

        if options:
            options_text = "\n\n".join(
                f"**`{option['name']}`** "
                f"{'(Wajib)' if option.get('required', False) else '(Opsional)'}\n"
                f"{option['description']}"
                for option in options
            )

            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    f"### Option\n{options_text}"
                )
            )

        usage = getattr(help_data, "USAGE", [])

        if usage:
            usage_text = "\n".join(
                f"- {item}"
                for item in usage
            )

            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    f"### Cara penggunaan\n{usage_text}"
                )
            )

        permissions = getattr(help_data, "PERMISSIONS", [])

        if permissions:
            permissions_text = "\n".join(
                f"- {permission}"
                for permission in permissions
            )

            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    f"### Permission\n{permissions_text}"
                )
            )

        examples = getattr(help_data, "EXAMPLES", [])

        if examples:
            examples_text = "\n\n".join(
                f"**{example['command']}**\n"
                f"{example['description']}"
                for example in examples
            )

            self.container.add_item(
                discord.ui.Separator()
            )

            self.container.add_item(
                discord.ui.TextDisplay(
                    f"### Contoh\n{examples_text}"
                )
            )

        self.container.add_item(
            discord.ui.Separator()
        )

        self.container.add_item(
            discord.ui.TextDisplay(
                "-# GrowLink • Help Center"
            )
        )
