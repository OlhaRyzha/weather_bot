import logging
from aiogram import Bot
from bot.db import init_mysql_pool
from bot.repositories import MySQLShortcutRepository, shortcuts_storage
from config.settings import MESSAGES, MYSQL


async def on_startup(bot: Bot):
    if not MYSQL.enabled:
        logging.info(MESSAGES["msql_disabled"])
        return

    pool = await init_mysql_pool()
    repo = MySQLShortcutRepository(pool)
    await repo.ensure_schema()
    shortcuts_storage.set_backend(repo)
    logging.info(MESSAGES["msql_ready"])
