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

help_kb = ReplyKeyboardBuilder()
commands = ['Криптовалюты', 'Подписка на крипту', 'Отменить подписку', 'Изменить подписку']
for command in commands:
    help_kb.add(types.KeyboardButton(text=command))
help_kb.adjust(2)


value_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="MIN"),
            types.KeyboardButton(text="MAX")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
    )


subscription_kb = ReplyKeyboardBuilder()
subscription_kb.row(
    types.KeyboardButton(text="Подписаться на крипту")
    )
subscription_kb.row(
    types.KeyboardButton(text="Изменить подписку"),
    types.KeyboardButton(text="Отменить подписку"),
    )
subscription_kb.row(
    types.KeyboardButton(text="Проверить подписку")
    )


plus_max_price_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="MAX"),
            types.KeyboardButton(text="Отмена")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
    )


plus_min_price_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="MIN"),
            types.KeyboardButton(text="Отмена")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
    )
