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
                if guild.id == 1028539778272084039:
                    # guild = await self.bot.fetch_guild(cfg.guild.guild_id)
                    for user in guild.get_role(cfg.roles.streamer).members:

                        print(user.activity.__class__)
                        if type(user.activity) == discord.activity.Streaming:
                            description = f"{user.mention} сейчас стримит, скорее заходи!\n{user.activity.url}"
                            # description = f"{user.activity.url}"
                            activity_created_timestamp = user.activity.created_at.timestamp()
                            now = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() / 1000,
                                                                  tz=datetime.timezone.utc).timestamp()
                            print(activity_created_timestamp)
                            print(now)
                            last_online = ((now - activity_created_timestamp) * 1000) % 3600
                            print(last_online)
                            if 0 <= last_online < 60:
                                await guild.system_channel.send(
                                    embed=discord.Embed(description=description, url="https://www.go.twitch.tv/nix"))

                    await asyncio.sleep(delay)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stream(bot))
