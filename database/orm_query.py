from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types

from database.models import Data

async def orm_add_subscription(session: AsyncSession, data: dict, message: types.Message):
    try:
        obj = Data(
            user_id = message.from_user.id,
            crypto = data['crypto'],
            max_val = data['max_val'],
            min_val = data['min_val']
            )
        session.add(obj)
        await session.commit()
        return
    except KeyError as error:
        print('1')

    try:
        obj = Data(
            user_id = message.from_user.id,
            crypto = data['crypto'],
            min_val = data['min_val']
            )
        session.add(obj)
        await session.commit()
        return
    except KeyError as error:
        print('2',error)
        obj = Data(
            user_id = message.from_user.id,
            crypto = data['crypto'],
            max_val = data['max_val']
            )
        session.add(obj)
        await session.commit()
        return


async def orm_get_subscriptions(session: AsyncSession):
    '''Посмотреть абсолютно все подписки, для админа.'''
    query = select(Data)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user_subscriptions(session: AsyncSession, message: types.Message):
    query = select(Data).where(Data.user_id == message.from_user.id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_user_subscription(session: AsyncSession, product_id: int):
    query = delete(Data).where(Data.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_subscription(session: AsyncSession, product_id: int, data):
    query = update(Data).where(Data.id == product_id).values(
        max_val = data['max_val'],
        min_val = data['min_val'])
    await session.execute(query)
    await session.commit()


async def orm_delete_subscription(session: AsyncSession, message: types.Message, crypto_name):
    query = delete(Data).where(Data.user_id == message.from_user.id,
                               Data.crypto == crypto_name)
    await session.execute(query)
    await session.commit()


async def orm_delete_subscription(session: AsyncSession, product_id: int):
    query = delete(Data).where(Data.id == product_id)
    await session.execute(query)
    await session.commit()


