import asyncio
import datetime
import re

import discord
from discord.ext import commands

from discord_bot.config import load_config

cfg = load_config()


class Stream(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._task = bot.loop.create_task(self.stream_checker())
        self.regex = re.compile(r"(?:https?://)?(?:www\.)?(?:go\.)?(?:twitch\.tv/)?(.+)")

    async def stream_checker(self):
        await self.bot.wait_until_ready()

        delay = 60
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                if guild.id == cfg.guild.guild_id:
                    # guild = await self.bot.fetch_guild(cfg.guild.guild_id)
                    for user in guild.get_role(cfg.roles.streamer).members:
                        if type(user.activity) == discord.activity.Streaming:
                            description = f"{user.mention} сейчас стримит, скорее заходи!\n{user.activity.url}"
                            # description = f"{user.activity.url}"
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
                                    url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{twitch_name}-1920x1080.jpg")
                                embed.set_author(
                                    name=user.name,
                                    icon_url=user.avatar.url
                                )
                                announcement_channel = guild.get_channel(cfg.channels.stream_channel)
                                announcement_role = guild.get_role(cfg.roles.twitch_announcement)
                                await announcement_channel.send(
                                    content=f'{announcement_role.mention}\n {user.mention} сейчас стримит, скорее '
                                            f'заходи посмотреть!',
                                    embed=embed
                                )

                    await asyncio.sleep(delay)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stream(bot))
