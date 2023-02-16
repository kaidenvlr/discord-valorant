from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.api.tracker_gg import tracker_embed
from utils.errors import ValorantBotError
from utils.valorant import cache as Cache
from utils.valorant.db import DATABASE
from utils.valorant.endpoint import API_ENDPOINT

if TYPE_CHECKING:
    from bot import ValorantBot


class Tracker(commands.Cog):
    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        self.endpoint: API_ENDPOINT = None
        self.db: DATABASE = None
        self.reload_cache.start()

    def cog_unload(self) -> None:
        self.reload_cache.cancel()

    @tasks.loop(minutes=30)
    async def reload_cache(self) -> None:
        """Reload the cache every 30 minutes"""
        self.funtion_reload_cache()

    def funtion_reload_cache(self, force=False) -> None:
        """Reload the cache"""
        with contextlib.suppress(Exception):
            cache = self.db.read_cache()
            valorant_version = Cache.get_valorant_version()
            if valorant_version != cache['valorant_version'] or force:
                Cache.get_cache()
                cache = self.db.read_cache()
                cache['valorant_version'] = valorant_version
                self.db.insert_cache(cache)
                print('Updated cache')

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """When the bot is ready"""
        self.db = DATABASE()
        self.endpoint = API_ENDPOINT()

    async def get_endpoint(
        self, user_id: int, locale_code: str = None, username: str = None, password: str = None
    ) -> API_ENDPOINT:
        """Get the endpoint for the user"""
        if username is not None and password is not None:
            auth = self.db.auth
            auth.locale_code = locale_code
            data = await auth.temp_auth(username, password)
        elif username or password:
            raise ValorantBotError(f"Please provide both username and password!")
        else:
            data = await self.db.is_data(user_id, locale_code)
        data['locale_code'] = locale_code
        endpoint = self.endpoint
        endpoint.activate(data)
        return endpoint

    @app_commands.command(name="tracker", description="Показать статистику игрока с tracker.gg")
    async def tracker(self, interaction: discord.Interaction, nickname: str, tag: str) -> None:
        await interaction.response.defer()
        response = tracker_embed(nickname, tag)
        if response['status'] == 'ok':
            await interaction.followup.send(embeds=response['embeds'])
        else:
            await interaction.followup.send(embed=response['embed'])


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Tracker(bot))
