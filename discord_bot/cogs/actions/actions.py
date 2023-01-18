import discord
from discord import app_commands
from discord.ext import commands

from discord_bot.config import load_config
from discord_bot.utils.api.actions.some_random_api import hug_gif, pat_gif
from discord_bot.utils.api.actions.tenor import Tenor


class Action(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cfg = load_config('.env')

    @app_commands.command(name="punch", description="Ударить указанного пользователя")
    @app_commands.describe(member="Упоминание пользователя")
    @app_commands.guild_only()
    async def punch(self, interaction: discord.Interaction, member: discord.Member):
        uri = Tenor('anime punch').find()
        embed = discord.Embed(
            color=0xa2b6a2,
            description=f'{interaction.user.mention} бьет {member.mention}'
        )
        embed.set_image(url=uri)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pat", description="Погладить по голове указанного пользователя")
    @app_commands.describe(member="Упоминание пользователя")
    @app_commands.guild_only()
    async def pat(self, interaction: discord.Interaction, member: discord.Member):
        uri = pat_gif()
        text = '{} гладит'.format(interaction.user.mention)
        text += ' {}!'.format(member.mention)
        embed = discord.Embed(color=0xa2b6a2, description=text)
        embed.set_image(url=uri)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Обнять указанного пользователя")
    @app_commands.describe(member="Упоминание пользователя")
    @app_commands.guild_only()
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        uri = hug_gif()
        text = '{} обнимает'.format(interaction.user.mention)
        text += ' {}!'.format(member.mention)
        embed = discord.Embed(color=0xa2b6a2, description=text)
        embed.set_image(url=uri)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Action(bot))
