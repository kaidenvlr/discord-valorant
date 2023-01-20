import discord
from discord.ext import commands
from discord.ui import Button, View

from discord_bot.config import load_config

cfg = load_config()


async def message(bot: commands.Bot):
    guild = bot.get_guild(cfg.guild.guild_id)
    announcement_channel = guild.get_channel(cfg.channels.stream_channel)

    button = Button(label="Получить роль", style=discord.ButtonStyle.success, emoji="👍")

    async def button_callback(interaction: discord.Interaction):
        if interaction.guild.get_role(cfg.roles.twitch_announcement) in interaction.user.roles:
            embed_callback = discord.Embed(description="У вас уже имеется эта роль", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed_callback, ephemeral=True)
        else:
            embed_callback = discord.Embed(description="Вы подписались на уведомления о стримах на сервере!",
                                           colour=discord.Colour.green())
            await interaction.user.add_roles(interaction.guild.get_role(cfg.roles.twitch_announcement))
            await interaction.response.send_message(embed=embed_callback, ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    embed = discord.Embed(
        title="Анонсы стримов",
        description="Эта роль позволит вам получать уведомления, если кто-то из сервера начинает стрим на твиче."
                    "Нажмите на кнопку под сообщением, чтобы бот выдал вам автоматически эту роль!",
        colour=discord.Colour.dark_purple()
    )

    await announcement_channel.send(embed=embed, view=view)
