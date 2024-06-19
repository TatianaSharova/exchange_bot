import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession

from handlers.user import user_canal_router
from handlers.user_subscription import user_subscription_router
from database.engine import create_db, drop_db, session_maker


API_TOKEN = os.getenv('TELEGRAM_TOKEN')
COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


logging.basicConfig(level=logging.INFO)


dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=API_TOKEN)
dp.include_router(user_subscription_router)
dp.include_router(user_canal_router)

async def on_startup(bot):

    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('бот выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)

    while True:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
