import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import select

from handlers.utils import get_crypto_price
load_dotenv()

from database.models import Data
from middlewares.db import DataBaseSession

from handlers.user import user_canal_router
from handlers.user_subscription import user_subscription_router
from database.engine import create_db, drop_db, session_maker
from bot_cmds_list import bot_cmds
from sqlalchemy.ext.asyncio import AsyncSession


API_TOKEN = os.getenv('TELEGRAM_TOKEN')
COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


logging.basicConfig(level=logging.INFO)


dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=API_TOKEN)
dp.include_router(user_subscription_router)
dp.include_router(user_canal_router)


# async def check_prices(session: AsyncSession, bot: Bot):
#     subscriptions = await session.execute(select(Data))
#     subscriptions = subscriptions.scalars().all()

#     for sub in subscriptions:
#         current_price = await get_crypto_price(sub.crypto)
#         if (sub.min_val and current_price <= sub.min_val) or (sub.max_val and current_price >= sub.max_val):
#             await bot.send_message(
#                     sub.user_id,
#                     f"Стоимость {sub.crypto} достигла цели! Цена в данный момент: ${current_price}"
#             )

#         await asyncio.sleep(60)

async def check_prices(session: AsyncSession, bot: Bot):
    while True:
        async with session_maker() as session:
            subscriptions = await session.execute(select(Data))
            subscriptions = subscriptions.scalars().all()

            for sub in subscriptions:
                current_price = get_crypto_price(sub.crypto)
                if (sub.min_val and current_price <= sub.min_val) or (sub.max_val and current_price >= sub.max_val):
                    message = f"Стоимость {sub.crypto} достигла цели! Цена в данный момент: ${current_price}"
                    if (sub.last_message and sub.last_message != message):
                        await bot.send_message(sub.user_id, message)
                        sub.last_message = message
                        session.add(sub)                                                 # TODO update
                        await session.commit()
            await asyncio.sleep(60)


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

    asyncio.create_task(check_prices(session_maker, bot))

    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands(commands=bot_cmds, scope=types.BotCommandScopeAllPrivateChats())

    while True:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
