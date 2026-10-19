import discord


class PromotionResultView(discord.ui.LayoutView):
    def __init__(self, success: bool):
        super().__init__(timeout=300)

        if success:
            message = (
                "## ✅ Promotion Submitted\n"
                "Your promotion has been submitted successfully!"
            )
            color = discord.Color.green()
        else:
            message = (
                "## ❌ Submission Failed\n"
                "Failed to submit your promotion. "
                "Please check the bot's permissions and try again."
            )
            color = discord.Color.red()

        self.add_item(
            discord.ui.Container(
                discord.ui.TextDisplay(message),
                accent_colour=color,
            )
        )