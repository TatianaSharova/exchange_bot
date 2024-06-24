from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Data(Base):
    '''
    Модель для хранения информации о подписке пользователя
    на определенную валюту.
    '''
    __tablename__ = 'data'

    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
    user_id: Mapped[str] = mapped_column(Integer, nullable=False)
    crypto: Mapped[str] = mapped_column(String(7))
    min_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_val: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
