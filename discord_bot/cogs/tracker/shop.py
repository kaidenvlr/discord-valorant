import discord
import mysql.connector
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from discord_bot.config import load_config
from discord_bot.utils.api.valorant.auth import Auth
from discord_bot.utils.api.valorant.skins import User

localization = {
    'uae': 'ar-ae',
    'germany': 'de-de',
    'england': 'en-us',
    'spain': 'es-es',
    'mexico': 'es-mx',
    'france': 'fr-fr',
    'indonesia': 'id-id',
    'italy': 'it-it',
    'japan': 'ja-jp',
    'korea': 'ko-kr',
    'poland': 'pl-pl',
    'brazil': 'pt-br',
    'russia': 'ru-ru',
    'thailand': 'th-th',
    'turkey': 'tr-tr',
    'vietnam': 'vi-vn',
    'china': 'zh-cn',
    'taiwan': 'zh-tw'
}


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = load_config(".env")

    @app_commands.command(name="shop", description="Посмотреть магазин в валоранте")
    @app_commands.describe(locale="Язык локализации")
    @app_commands.choices(locale=[
        Choice(name=f'{i}', value=f'{localization[i]}') for i in localization.keys()
    ])
    async def shop(self, interaction: discord.Interaction, locale: Choice[str]):
        await interaction.response.send_message(content="чекаю магазин...")
        conn = mysql.connector.connect(
            host=self.cfg.db.hostname,
            username=self.cfg.db.username,
            password=self.cfg.db.password,
            database=self.cfg.db.database
        )

        cursor = conn.cursor()
        cursor.execute(
            f'select username, password from user where uid = "{interaction.user.id}"'
        )
        result = cursor.fetchone()
        conn.close()

        if result is None:
            embed = discord.Embed(
                color=discord.Color.red(),
                description="Добавьте свои данные для входа, чтобы проверить магазин."
                            "Для этого используйте /login."
            )
            await interaction.edit_original_response(content="", embed=embed)
        else:
            username = result[0]
            password = result[1]

            user = Auth(username, password)
            user_data = user.get_data()
            if type(user_data) != type({'error': 'error'}):
                access_token = user_data[0]
                entitlements_token = user_data[1]
                user_id = user_data[2]
                user = User(entitlements_token, access_token, user_id)

                skin_data = user.skins(locale=locale.value)

                skins = skin_data[0]
                remaining = skin_data[1]

                try:
                    title = f"До обновления магазина осталось: {remaining // 3600} часов " \
                            f"{remaining // 60 % 60} минут {remaining % 60} секунд" if remaining // 3600 > 0 else \
                        f"{remaining // 60 % 60} минут {remaining % 60} секунд"
                    embeds = []
                    for skin in skins:
                        match skin['tier_id']:
                            case '60bca009-4182-7998-dee7-b8a2558dc369':
                                c = discord.Color.dark_magenta()
                            case '12683d76-48d7-84a3-4e09-6985794f0445':
                                c = discord.Color.blue()
                            case 'e046854e-406c-37f4-6607-19a9ba8426fc':
                                c = discord.Color.orange()
                            case '0cebb8be-46d7-c12a-d306-e9907bfc5a25':
                                c = discord.Color.teal()
                            case '411e4a55-4e59-7757-41f0-86a53f101bb5':
                                c = discord.Color.gold()
                            case _:
                                c = discord.Color.default()
                        embed = discord.Embed(
                            title=f"{skin['name']} стоит {skin['price']}",
                            color=c
                        )
                        embed.set_thumbnail(url=skin['tier'])
                        embed.set_image(url=skin['image'])

                        embeds.append(embed)

                    await interaction.edit_original_response(content=title, embeds=embeds)

                except TypeError:
                    embed = discord.Embed(
                        title="Ошибка при получении текущего магазина")
                    await interaction.edit_original_response(content="", embed=embed)
            else:
                embed = discord.Embed(title=user_data['message'])
                await interaction.edit_original_response(content="", embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
