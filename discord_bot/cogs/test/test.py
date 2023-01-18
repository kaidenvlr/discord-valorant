import discord
from discord import app_commands
from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="test", description="Тест функция")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Успешно!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
