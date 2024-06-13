from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Криптовалюты"),
            types.KeyboardButton(text="Помощь")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
    )

crypto_kb = ReplyKeyboardBuilder()
crypto_symbols = ['BTC', 'ETH', 'USDT', 'LTC', 'XLM', 'SOL', 'BNB', 'NOT', 'TON']
for crypto in crypto_symbols:
    crypto_kb.add(types.KeyboardButton(text=crypto))
crypto_kb.adjust(3)

help_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Криптовалюты"),
            types.KeyboardButton(text="Подписка на крипту")
        ]
    ],
    resize_keyboard=True,
    # one_time_keyboard=True
    )
