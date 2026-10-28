
import discord

from database.growlink.emoji_manager import (
    get_emojis,
    get_emoji,
)


class EmojiListView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=180)

        emojis = get_emojis()

        container_items = [
            discord.ui.TextDisplay(
                "## 🧩 GrowLink Emoji List"
            ),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay(
                "**How to use**\n"
                "Type an emoji key surrounded by colons in your "
                "World Name or Description.\n\n"
                "Example: `:dirt:`\n"
                "If the emoji exists, GrowLink will replace it "
                "with the corresponding custom emoji. "
                "Otherwise, the text remains unchanged."
            ),
            discord.ui.Separator(visible=True),
            discord.ui.TextDisplay("**Available Emojis**"),
        ]

        if emojis:
            emoji_lines = [
                f"{get_emoji(key, default=f':{key}:')} `:{key}:`"
                for key in sorted(emojis)
            ]

            chunks = []
            current_chunk = []

            for line in emoji_lines:
                candidate = "\n".join(current_chunk + [line])

                if len(candidate) > 3500 and current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)

            if current_chunk:
                chunks.append("\n".join(current_chunk))

            for chunk in chunks:
                container_items.append(
                    discord.ui.TextDisplay(chunk)
                )
        else:
            container_items.append(
                discord.ui.TextDisplay(
                    "No emojis are currently available."
                )
            )

        container_items.extend(
            [
                discord.ui.Separator(visible=True),
                discord.ui.TextDisplay(
                    "-# Emoji list is loaded from the current cache."
                ),
            ]
        )

        self.add_item(
            discord.ui.Container(
                *container_items,
                accent_colour=discord.Color.green(),
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
