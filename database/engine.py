import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from database.models import Base

load_dotenv()


engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession,
                                   expire_on_commit=False)


async def create_db():
    '''Создает базу данных.'''
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    '''Удаляет базу данных.'''
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
