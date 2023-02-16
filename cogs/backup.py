from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

from utils.backup.db_insert import backup_notify, backup_cookie, backup_users

if TYPE_CHECKING:
    from bot import ValorantBot


class Backup(commands.Cog):
    def __init__(self, bot: ValorantBot):
        self.bot: ValorantBot = bot

    @commands.command()
    @commands.is_owner()
    async def backup(self, ctx: commands.Context) -> None:
        async with ctx.typing():
            print("backup started...")

            backup_users()
            backup_cookie()
            backup_notify()

            await ctx.reply("backup succeeded")


async def setup(bot: ValorantBot) -> None:
    await bot.add_cog(Backup(bot))
