import discord
import mysql.connector
from discord import app_commands
from discord.ext import commands

from discord_bot.config import load_config


class Logout(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = load_config(".env")

    @app_commands.command(name="logout", description="Удалить данные об аккаунте из базы")
    async def logout(self, interaction):
        await interaction.response.send_message(
            content="Данные удаляются из базы...", ephemeral=True
        )

        conn = mysql.connector.connect(
            host=self.cfg.db.hostname,
            username=self.cfg.db.username,
            password=self.cfg.db.password,
            database=self.cfg.db.database
        )

        cursor = conn.cursor()

        cursor.execute(f'select * from user where uid = "{interaction.user.id}"')
        if cursor.fetchone() is None:
            action = "Ваших данных еще нет в нашей базе данных для авторизации"
        else:
            cursor.execute(
                f'delete from user where uid = "{interaction.user.id}"'
            )
            action = "Вы успешно удалили свои данные для авторизации из базы данных :white_check_mark:"

        conn.commit()
        conn.close()

        embed = discord.Embed(
            color=discord.Color.dark_red(),
            description=action
        )

        await interaction.edit_original_response(content="", embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logout(bot))
