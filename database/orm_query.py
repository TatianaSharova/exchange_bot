from aiogram import types
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Data


async def orm_add_subscription(session: AsyncSession,
                               data: dict, message: types.Message):
    '''Создание подписки.'''
    obj = Data(
        user_id=message.from_user.id,
        crypto=data['crypto'],
        max_val=data['max_val'],
        min_val=data['min_val']
        )
    session.add(obj)
    await session.commit()


async def orm_add_subscription_min(session: AsyncSession,
                                   data: dict, message: types.Message):
    '''Создание подписки только с MIN значением.'''
    obj = Data(
        user_id=message.from_user.id,
        crypto=data['crypto'],
        min_val=data['min_val']
        )
    session.add(obj)
    await session.commit()


async def orm_add_subscription_max(session: AsyncSession,
                                   data: dict, message: types.Message):
    '''Создание подписки только с MAX значением.'''
    obj = Data(
        user_id=message.from_user.id,
        crypto=data['crypto'],
        max_val=data['max_val']
        )
    session.add(obj)
    await session.commit()


async def orm_get_subscriptions(session: AsyncSession):
    '''Получить абсолютно все подписки, для админа.'''
    query = select(Data)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user_subscriptions(session: AsyncSession,
                                     message: types.Message):
    '''Получить все подписки определенного пользователя.'''
    query = select(Data).where(Data.user_id == message.from_user.id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user_subscription(session: AsyncSession, product_id: int):
    '''Получить определенную подписку пользователя.'''
    query = select(Data).where(Data.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_subscription(session: AsyncSession,
                                  product_id: int, data):
    '''Обновить выбранную подписку.'''
    try:
        query = update(Data).where(Data.id == product_id).values(
            max_val=data['max_val'],
            min_val=data['min_val'],
            last_message=None)
    except KeyError:
        try:
            query = update(Data).where(Data.id == product_id).values(
                max_val=data['max_val'],
                last_message=None)
        except KeyError:
            query = update(Data).where(Data.id == product_id).values(
                min_val=data['min_val'],
                last_message=None)
    finally:
        await session.execute(query)
        await session.commit()


async def orm_delete_subscription(session: AsyncSession, product_id: int):
    '''Удалить выбранную подписку.'''
    query = delete(Data).where(Data.id == product_id)
    await session.execute(query)
    await session.commit()
