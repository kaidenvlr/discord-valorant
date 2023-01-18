import discord
from discord import app_commands
from discord.ext import commands

from discord_bot.config import load_config
from discord_bot.utils.api.valorant.stats import Player


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = load_config(".env")

    @app_commands.command(name="stats", description="Посмотреть статистику за последние 5 матчей")
    @app_commands.describe(nickname="Никнейм игрока", tag="Тег игрока")
    async def logout(self, interaction, nickname: str, tag: str):
        await interaction.response.send_message('Ведется подсчет статистики, пожалуйста подождите...')
        tagline = tag
        player = Player(nickname, tagline)
        result = player.stats()

        if result['status'] == 'ok':
            embed = discord.Embed(
                title=f"Статистика игрока {nickname}#{tagline} за последние 5 матчей",
                description=f"Текущий ранг: {result['rank']}: {result['elo']}\nСредний урон за "
                            f"раунд: {result['adr']}\nСредний счет матча: {result['acs']}\nСоотношение "
                            f"убийств к смертям: {result['kd']}",
                colour=discord.Color.dark_purple())
            embed.set_thumbnail(url=result['img_url'])
        else:
            embed = discord.Embed(
                title='Произошла ошибка при подсчете статистики игрока')

        await interaction.edit_original_response(content="", embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Stats(bot))
