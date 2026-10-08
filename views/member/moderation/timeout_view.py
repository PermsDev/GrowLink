import re

import discord


class RemoveTimeoutButton(
    discord.ui.DynamicItem[
        discord.ui.Button
    ],
    template=r"moderation:remove_timeout:(?P<guild_id>\d+):(?P<member_id>\d+)",
):

    def __init__(
        self,
        guild_id: int,
        member_id: int,
    ):
        self.guild_id = guild_id
        self.member_id = member_id

        super().__init__(
            discord.ui.Button(
                label="Remove Timeout",
                style=discord.ButtonStyle.success,
                custom_id=(
                    f"moderation:remove_timeout:"
                    f"{guild_id}:{member_id}"
                ),
            )
        )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: discord.ui.Button,
        match: re.Match[str],
    ):

        return cls(
            guild_id=int(
                match.group("guild_id")
            ),
            member_id=int(
                match.group("member_id")
            ),
        )

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        if interaction.user.id != self.member_id:

            await interaction.response.send_message(
                "You cannot use this button.",
                ephemeral=True,
            )

            return

        guild = interaction.client.get_guild(
            self.guild_id
        )

        if guild is None:

            await interaction.response.send_message(
                "The server could not be found.",
                ephemeral=True,
            )

            return

        member = guild.get_member(
            self.member_id
        )

        if member is None:

            try:

                member = await guild.fetch_member(
                    self.member_id
                )

            except discord.HTTPException:

                await interaction.response.send_message(
                    "The user could not be found in the server.",
                    ephemeral=True,
                )

                return

        try:

            await member.timeout(
                None,
                reason="Timeout removed by the user.",
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "The bot does not have permission to remove the timeout.",
                ephemeral=True,
            )

            return

        except discord.HTTPException:

            await interaction.response.send_message(
                "Failed to remove the timeout.",
                ephemeral=True,
            )

            return

        self.item.disabled = True

        await interaction.response.edit_message(
            content="Your timeout has been removed.",
            view=self.view,
        )


class TimeoutView(
    discord.ui.View
):

    def __init__(
        self,
        guild_id: int,
        member_id: int,
    ):
        super().__init__(
            timeout=None
        )

        self.add_item(
            RemoveTimeoutButton(
                guild_id=guild_id,
                member_id=member_id,
            )
        )