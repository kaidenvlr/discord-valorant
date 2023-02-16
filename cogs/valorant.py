from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Literal  # noqa: F401

from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING

from utils.checks import owner_only
from utils.errors import ValorantBotError
from utils.locale_v2 import ValorantTranslator
from utils.valorant import cache as Cache, useful, view as View
from utils.valorant.db import DATABASE
from utils.valorant.embed import Embed, GetEmbed
from utils.valorant.endpoint import API_ENDPOINT
from utils.valorant.local import ResponseLanguage
from utils.valorant.resources import setup_emoji

VLR_locale = ValorantTranslator()

if TYPE_CHECKING:
    from bot import ValorantBot


class ValorantCog(commands.Cog, name='Valorant'):
    """Valorant API Commands"""

    def __init__(self, bot: ValorantBot) -> None:
        self.bot: ValorantBot = bot
        self.endpoint: API_ENDPOINT = None
        self.db: DATABASE = None
        self.reload_cache.start()

    def cog_unload(self) -> None:
        self.reload_cache.cancel()

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

    @tasks.loop(minutes=30)
    async def reload_cache(self) -> None:
        """Reload the cache every 30 minutes"""
        self.funtion_reload_cache()

    @reload_cache.before_loop
    async def before_reload_cache(self) -> None:
        """Wait for the bot to be ready before reloading the cache"""
        await self.bot.wait_until_ready()

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

    @app_commands.command(description='Вход в Riot аккаунт')
    @app_commands.describe(username='Логин', password='Пароль')
    # @dynamic_cooldown(cooldown_5s)
    async def login(self, interaction: Interaction, username: str, password: str) -> None:
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        auth = self.db.auth
        auth.locale_code = interaction.locale
        authenticate = await auth.authenticate(username, password)

        if authenticate['auth'] == 'response':
            await interaction.response.defer(ephemeral=True)
            login = await self.db.login(user_id, authenticate, interaction.locale)

            if login['auth']:
                embed = Embed(f"{response.get('SUCCESS')} **{login['player']}!**")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            raise ValorantBotError(f"{response.get('FAILED')}")

        elif authenticate['auth'] == '2fa':
            cookies = authenticate['cookie']
            message = authenticate['message']
            label = authenticate['label']
            modal = View.TwoFA_UI(interaction, self.db, cookies, message, label, response)
            await interaction.response.send_modal(modal)

    @app_commands.command(description='Выход и удаление аккаута из базы')
    # @dynamic_cooldown(cooldown_5s)
    async def logout(self, interaction: Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        user_id = interaction.user.id
        if logout := self.db.logout(user_id, interaction.locale):
            if logout:
                embed = Embed(response.get('SUCCESS'))
                return await interaction.followup.send(embed=embed, ephemeral=True)
            raise ValorantBotError(response.get('FAILED'))

    @app_commands.command(description="Показывает ваш магазин на сегодня")
    @app_commands.describe(username='Логин аккаунта (без входа)', password='Пароль аккаунта (без входа)')
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def store(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # language
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        # setup emoji
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # get endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # fetch skin price
        skin_price = endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = endpoint.store_fetch_storefront()
        embeds = GetEmbed.store(endpoint.player, data, response, self.bot)
        await interaction.followup.send(
            embeds=embeds, view=View.share_button(interaction, embeds) if is_private_message else MISSING
        )

    @app_commands.command(description='Показывает ваши Valorant Points и Radianite Points')
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def point(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # setup emoji
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, locale_code=interaction.locale)

        # data
        data = endpoint.store_fetch_wallet()
        embed = GetEmbed.point(endpoint.player, data, response, self.bot)

        await interaction.followup.send(
            embed=embed, view=View.share_button(interaction, [embed]) if is_private_message else MISSING
        )

    @app_commands.command(description='Показывает ваш прогресс по ежедневным и еженедельным миссиям')
    # @dynamic_cooldown(cooldown_5s)
    async def mission(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # data
        data = endpoint.fetch_contracts()
        embed = GetEmbed.mission(endpoint.player, data, response)

        await interaction.followup.send(
            embed=embed, view=View.share_button(interaction, [embed]) if is_private_message else MISSING
        )

    @app_commands.command(description='Показывает ваш найтмаркет')
    # @dynamic_cooldown(cooldown_5s)
    async def nightmarket(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        # setup emoji
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # language
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # fetch skin price
        skin_price = endpoint.store_fetch_offers()
        self.db.insert_skin_price(skin_price)

        # data
        data = endpoint.store_fetch_storefront()
        embeds = GetEmbed.nightmarket(endpoint.player, data, self.bot, response)

        await interaction.followup.send(
            embeds=embeds, view=View.share_button(interaction, embeds) if is_private_message else MISSING
        )

    @app_commands.command(description='Показывает прогресс баттлпасса')
    # @dynamic_cooldown(cooldown_5s)
    async def battlepass(self, interaction: Interaction, username: str = None, password: str = None) -> None:

        # check if user is logged in
        is_private_message = True if username is not None or password is not None else False

        await interaction.response.defer(ephemeral=is_private_message)

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale, username, password)

        # data
        data = endpoint.fetch_contracts()
        content = endpoint.fetch_content()
        season = useful.get_season_by_content(content)

        embed = GetEmbed.battlepass(endpoint.player, data, season, response)

        await interaction.followup.send(
            embed=embed, view=View.share_button(interaction, [embed]) if is_private_message else MISSING
        )

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Посмотреть определенный бандл")
    @app_commands.describe(bundle="Название бандла")
    @app_commands.guild_only()
    # @dynamic_cooldown(cooldown_5s)
    async def bundle(self, interaction: Interaction, bundle: str) -> None:

        await interaction.response.defer()

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # setup emoji
        await setup_emoji(self.bot, interaction.guild, interaction.locale)

        # cache
        cache = self.db.read_cache()

        # default language language
        default_language = 'ru-RU'

        # find bundle
        find_bundle_en_US = [
            cache['bundles'][i]
            for i in cache['bundles']
            if bundle.lower() in cache['bundles'][i]['names'][default_language].lower()
        ]
        find_bundle_locale = [
            cache['bundles'][i]
            for i in cache['bundles']
            if bundle.lower() in cache['bundles'][i]['names'][str(VLR_locale)].lower()
        ]
        find_bundle = find_bundle_en_US if len(find_bundle_en_US) > 0 else find_bundle_locale

        # bundle view
        view = View.BaseBundle(interaction, find_bundle, response)
        await view.start()

    # inspired by https://github.com/giorgi-o
    @app_commands.command(description="Показывает текущие доступные бандлы")
    # @dynamic_cooldown(cooldown_5s)
    async def bundles(self, interaction: Interaction) -> None:

        await interaction.response.defer()

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        # endpoint
        endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)

        # data
        bundle_entries = endpoint.store_fetch_storefront()

        # bundle view
        view = View.BaseBundle(interaction, bundle_entries, response)
        await view.start_furture()

    # credit https://github.com/giorgi-o
    # https://github.com/giorgi-o/SkinPeek/wiki/How-to-get-your-Riot-cookies
    @app_commands.command()
    @app_commands.describe(cookie="Ваши куки-данные")
    async def cookies(self, interaction: Interaction, cookie: str) -> None:
        """Login to your account with a cookie"""

        await interaction.response.defer(ephemeral=True)

        # language
        response = ResponseLanguage(interaction.command.name, interaction.locale)

        login = await self.db.cookie_login(interaction.user.id, cookie, interaction.locale)

        if login['auth']:
            embed = Embed(f"{response.get('SUCCESS')} **{login['player']}!**")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        view = ui.View()
        view.add_item(ui.Button(label="Tutorial", emoji="🔗", url="https://youtu.be/cFMNHEHEp2A"))
        await interaction.followup.send(f"{response.get('FAILURE')}", view=view, ephemeral=True)

    # ---------- ROAD MAP ---------- #

    # @app_commands.command()
    # async def contract(self, interaction: Interaction) -> None:
    #     # change agent contract

    # @app_commands.command()
    # async def party(self, interaction: Interaction) -> None:
    #     # curren party
    #     # pick agent
    #     # current map

    # @app_commands.command()
    # async def career(self, interaction: Interaction) -> None:
    #     # match history

    # ---------- DEBUGs ---------- #

    @app_commands.command(description='дебаг функция')
    @app_commands.describe(bug="баг, который хотите пофиксить")
    @app_commands.guild_only()
    @owner_only()
    async def debug(
        self, interaction: Interaction, bug: Literal['Skin price not loading', 'Emoji not loading', 'Cache not loading']
    ) -> None:

        await interaction.response.defer(ephemeral=True)

        response = ResponseLanguage(interaction.command.name, interaction.locale)

        if bug == 'Skin price not loading':
            # endpoint
            endpoint = await self.get_endpoint(interaction.user.id, interaction.locale)

            # fetch skin price
            skin_price = endpoint.store_fetch_offers()
            self.db.insert_skin_price(skin_price, force=True)

        elif bug == 'Emoji not loading':
            await setup_emoji(self.bot, interaction.guild, interaction.locale, force=True)

        elif bug == 'Cache not loading':
            self.funtion_reload_cache(force=True)

        success = response.get('SUCCESS')
        await interaction.followup.send(embed=Embed(success.format(bug=bug)))


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(ValorantCog(bot))
