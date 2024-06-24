import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import create_db, drop_db, session_maker
from database.models import Data
from handlers.user import user_canal_router
from handlers.user_subscription import user_subscription_router
from handlers.utils import get_crypto_price
from keyboards.bot_cmds_list import bot_cmds
from middlewares.db import DataBaseSession

load_dotenv()


API_TOKEN = os.getenv('TELEGRAM_TOKEN')
COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = os.getenv('COINMARKETCAP_URL')
AUTHOR_ID = os.getenv('AUTHOR_TELEGRAM_ID')


logging.basicConfig(level=logging.INFO)


dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=API_TOKEN)
dp.include_router(user_subscription_router)
dp.include_router(user_canal_router)


async def check_prices(session: AsyncSession, bot: Bot):
    '''
    Присылает сообщение пользователю, если цена криптовалюты достигла значений,
    на которые он подписан.
    '''
    while True:
        async with session_maker() as session:
            subscriptions = await session.execute(select(Data))
            subscriptions = subscriptions.scalars().all()

            for sub in subscriptions:
                current_price = get_crypto_price(sub.crypto)
                if sub.min_val and float(current_price) <= sub.min_val:
                    last_message_about = 'MIN'
                    if sub.last_message != last_message_about:
                        await bot.send_message(
                            sub.user_id,
                            f'Стоимость {sub.crypto} достигла нижнего '
                            f'порога в ${sub.min_val}!\n'
                            f'Цена в данный момент: ${current_price}')
                        sub.last_message = last_message_about
                        session.add(sub)
                        await session.commit()
                if sub.max_val and float(current_price) >= sub.max_val:
                    last_message_about = 'MAX'
                    if sub.last_message != last_message_about:
                        await bot.send_message(
                            sub.user_id,
                            f'Стоимость {sub.crypto} достигла верхнего '
                            f'порога в ${sub.max_val}!\n'
                            f'Цена в данный момент: ${current_price}')
                        sub.last_message = last_message_about
                        session.add(sub)
                        await session.commit()

            await asyncio.sleep(60)


async def on_startup(bot):
    '''Запускает БД.'''

    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('Бот выключен.')


async def main():
    '''Запуск бота.'''
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    asyncio.create_task(check_prices(session_maker, bot))

    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands(commands=bot_cmds,
                              scope=types.BotCommandScopeAllPrivateChats())

    while True:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
