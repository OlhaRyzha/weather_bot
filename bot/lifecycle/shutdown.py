from aiogram import Bot

from bot.db import close_mysql_pool


async def on_shutdown(bot: Bot):
    await close_mysql_pool()
