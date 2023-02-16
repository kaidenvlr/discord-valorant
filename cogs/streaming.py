from __future__ import annotations

import asyncio
import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View

cfg = {
    'guild_id': 942045817685045258,
    'streamer_role': 1065877033017675816,
    'fan_role': 1065576582397317182,
    'channel': 1065900893746245642,
}

if TYPE_CHECKING:
    from bot import ValorantBot


class Stream(commands.Cog):
    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        self.streaming.start()

    def cog_unload(self) -> None:
        self.streaming.cancel()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        guild = self.bot.get_guild(cfg['guild_id'])
        announcement_channel = guild.get_channel(cfg['channel'])

        await announcement_channel.purge(limit=100)

        button = Button(label="Получить роль", style=discord.ButtonStyle.success, emoji="👍")

        async def button_callback(interaction: discord.Interaction):
            if interaction.guild.get_role(cfg['fan_role']) in interaction.user.roles:
                embed_callback = discord.Embed(description="У вас уже имеется эта роль", colour=discord.Colour.red())
                await interaction.response.send_message(embed=embed_callback, ephemeral=True)
            else:
                embed_callback = discord.Embed(description="Вы подписались на уведомления о стримах на сервере!",
                                               colour=discord.Colour.green())
                await interaction.user.add_roles(interaction.guild.get_role(cfg['fan_role']))
                await interaction.response.send_message(embed=embed_callback, ephemeral=True)

        button.callback = button_callback
        view = View(timeout=None)
        view.add_item(button)
        embed = discord.Embed(
            title="Анонсы стримов",
            description="Эта роль позволит вам получать уведомления, если кто-то из сервера начинает стрим на твиче."
                        "Нажмите на кнопку под сообщением, чтобы бот выдал вам автоматически эту роль!",
            colour=discord.Colour.dark_purple()
        )

        await announcement_channel.send(embed=embed, view=view)

    @tasks.loop(minutes=10)
    async def streaming(self) -> None:
        await self.stream_checker()

    @streaming.before_loop
    async def before_streamers(self) -> None:
        await self.bot.wait_until_ready()
        print("Checking is someone is streaming now...")

    async def stream_checker(self):
        for guild in self.bot.guilds:
            if guild.id == cfg['guild_id']:
                for user in guild.get_role(cfg['streamer_role']).members:
                    if type(user.activity) == discord.activity.Streaming:
                        activity_created_timestamp = user.activity.created_at.timestamp()
                        now = datetime.datetime.utcnow().timestamp()
                        twitch_name = user.activity.assets['large_image'].split(':')[1]
                        last_online = (now - activity_created_timestamp) % 3600
                        print(datetime.datetime.fromtimestamp(now), last_online, sep="\t")
                        if 0 <= last_online < 60:
                            embed = discord.Embed(
                                title=user.activity.name,
                                url=user.activity.url
                            )
                            embed.add_field(
                                name="",
                                value=f"Играет в {user.activity.game}"
                            )
                            embed.set_thumbnail(
                                url=user.avatar.url
                            )
                            embed.set_image(
                                url=f"https://static-cdn.jtvnw.net/previews-ttv/"
                                    f"live_user_{twitch_name}-1920x1080.jpg")
                            embed.set_author(
                                name=user.name,
                                icon_url=user.avatar.url
                            )
                            announcement_channel = guild.get_channel(cfg['channel'])
                            announcement_role = guild.get_role(cfg['fan_role'])
                            await announcement_channel.send(
                                content=f'{announcement_role.mention}\n {user.mention} сейчас стримит, скорее '
                                        f'заходи посмотреть!',
                                embed=embed
                            )
                await asyncio.sleep(3)


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Stream(bot))
