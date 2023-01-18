import discord
import mysql.connector
from discord import app_commands
from discord.ext import commands

from discord_bot.config import load_config


class Login(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = load_config(".env")

    @app_commands.command(name="login", description="Внести данные об аккаунте (логин, пароль) в базу")
    @app_commands.describe(
        username="Логин аккаунта (без входа)",
        password="Пароль аккаунта (без входа)"
    )
    async def login(self, interaction, username: str, password: str):
        await interaction.response.send_message(
            content="Данные заносятся в базу...", ephemeral=True
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
            cursor.execute(
                f'insert into user values ("{interaction.user.id}", "{username}", "{password}")'
            )
            action = "добавили"
        else:
            cursor.execute(
                f'update user set username = "{username}", password = "{password}" where uid = "{interaction.user.id}"'
            )
            action = "обновили"

        conn.commit()
        conn.close()

        embed = discord.Embed(
            color=discord.Color.dark_blue(),
            description="Вы успешно " + action + " свои данные для авторизации в базе данных :white_check_mark:"
        )

        await interaction.edit_original_response(content="", embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Login(bot))
