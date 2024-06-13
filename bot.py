import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
from handlers.user import user_canal_router

load_dotenv(find_dotenv())

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


logging.basicConfig(level=logging.INFO)


dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=API_TOKEN)
dp.include_router(user_canal_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    while True:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
