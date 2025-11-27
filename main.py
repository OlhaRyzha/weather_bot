import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.lifecycle import on_shutdown, on_startup
from bot.routers import router
from config.settings import API_TOKEN


logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
