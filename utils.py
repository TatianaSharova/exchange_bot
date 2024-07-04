from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Data
from database.orm_query import orm_delete_user


async def send_message_or_delete_banned_user(
        session: AsyncSession, bot: Bot, sub: Data, last_message_about,
        current_price, message):
    if sub.last_message != last_message_about:
        try:
            await bot.send_message(sub.user_id, message)
            sub.last_message = last_message_about
            session.add(sub)
            await session.commit()
        except TelegramForbiddenError:
            await orm_delete_user(session, sub.user_id)
