import discord
from discord import app_commands
from discord.ext import commands

from discord_bot.config import load_config

cfg = load_config()


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def check_permissions(interaction: discord.Interaction) -> bool:
        return interaction.guild.get_role(cfg.roles.admin) in interaction.user.roles

    @app_commands.command(name="kick")
    @app_commands.describe(member="Упоминание пользователя")
    @app_commands.guild_only()
    @app_commands.check(check_permissions)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await interaction.response.send_message(
            content=f"пользователь {member.mention} был кикнут с сервера"
        )
        await interaction.guild.kick(member, reason=reason)

    @app_commands.command(name="ban")
    @app_commands.describe(
        member="Упоминание пользователя",
        reason="Причина бана"
    )
    @app_commands.guild_only()
    @app_commands.check(check_permissions)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await interaction.response.send_message(
            content=f"пользователь {member.mention} был забанен на сервере"
        )
        await interaction.guild.ban(member, reason=reason)

    @app_commands.command(name="clear_messages")
    @app_commands.describe(
        count="Количество сообщений"
    )
    @app_commands.guild_only()
    @app_commands.check(check_permissions)
    async def clear_messages(self, interaction: discord.Interaction, count: int):
        await interaction.response.send_message(
            content=f"Было очищено {count} сообщений :white_check_mark:",
            ephemeral=True
        )
        await interaction.channel.purge(limit=count)
