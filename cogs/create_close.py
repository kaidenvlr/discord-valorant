from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot import ValorantBot


class Event(commands.Cog):
    def __init__(self, bot: ValorantBot) -> None:
        self.bot = bot
        self.close_moderator_role = 1065113559832469524

    def check_close_moderator(self, interaction: discord.Interaction) -> bool:
        return interaction.guild.get_role(self.close_moderator_role) in interaction.user.roles

    @app_commands.command(name="create_event", description="Создать событие")
    @app_commands.describe(
        month="Номер месяца",
        day="День месяца",
        hour="В какой час",
        minute="В какую минуту",
        channel_id="ID канала, в котором будет ивента",
        name="Название ивента"
    )
    @app_commands.guild_only()
    async def create_event(
            self,
            interaction: discord.Interaction,
            month: int,
            day: int,
            hour: int,
            minute: int,
            channel_id: str,
            name: str = "5x5"
    ):
        if self.check_close_moderator(interaction):
            event = await interaction.guild.create_scheduled_event(
                name=name,
                description="",
                channel=interaction.guild.get_channel(int(channel_id)),
                start_time=datetime(datetime.now().year, month, day, hour, minute, 0, 0).astimezone()
            )
            await interaction.response.send_message(
                content=f"@everyone \n {event.url}"
            )


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Event(bot))
