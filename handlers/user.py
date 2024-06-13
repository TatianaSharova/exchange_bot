import os

import requests
from aiogram import F, Router, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from exceptions import HTTPResponseParsingError
from keyboards import reply
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

load_dotenv()

COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


user_canal_router = Router()


@user_canal_router.message(CommandStart())
async def send_welcome(message: types.Message) -> types.Message:
    await message.answer(
        "Привет! Я бот, который может предоставить информацию о стоимости выбранной криптовалюты в USD.\n"
        "Нажми на кнопку <Криптовалюты>, чтобы перейти к нужной криптовалюте.\n"
        "Если хочешь ознакомиться со всеми функциями бота, нажми на кнопку <Помощь>."
        )

    await message.answer("Выберите опцию:", reply_markup=reply.start_kb)


@user_canal_router.message(F.text.lower() == "криптовалюты")
async def offer_famous_crypto(message: types.Message):
    await message.reply(
        "Выбери необходимую криптовалюту.\n"
        "Если нужной криптовалюты нет в списке, "
        "отправь боту сообщение с коротким названием криптовалюты, "
        "например, BTC или USDT."
        )

    await message.answer(
        "Выберите криптовалюту:",
        reply_markup=reply.crypto_kb.as_markup(resize_keyboard=True),
    )


@user_canal_router.message(F.text.lower() == "помощь")
async def get_help(message: types.Message):
    await message.answer(
        "Этот бот может:\n"
        "1. Посмотреть стоимость выбранной крипты в USD.\n"
        "Для этого нажми кнопку <Криптовалюты>.\n"
        "2. Начать отслеживать курс отдельных криптовалют, "
        "присылая уведомления, когда курс достигает выбранных вами значений.\n"
        "Для этого нажми на кнопку <Подписка на крипту>."
        )

    await message.answer("Выберите:", reply_markup=reply.help_kb)


@user_canal_router.message(F.text.strip().lower() == "подписка на крипту")
async def follow_crypto(message: types.Message):
    await message.answer("Раздел пока в работе.")


@user_canal_router.message(F.text)
async def send_crypto_price(message: types.Message):
    crypto_name = message.text.strip().upper()
    if len(crypto_name) > 7:
        await message.reply("Слишком длинное название. "
                            "Проверьте правильность названия "
                            "и попробуйте снова.")
    else:
        price = get_crypto_price(crypto_name)

        if price:
            await message.reply(f"Стоимость {crypto_name} в USD: ${price}")
        else:
            await message.reply(
                f"Не удалось получить информацию о стоимости {crypto_name}. "
                f"Проверьте правильность названия и попробуйте снова.")


def get_crypto_price(crypto_name):
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
    }
    params = {
        'symbol': crypto_name,
        'convert': 'USD'
    }

    try:
        response = requests.get(COINMARKETCAP_URL,
                                headers=headers,
                                params=params)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        raise Exception(e)                                                           #TODO Exception

    if response.status_code == 200:
        try:
            data = response.json()
        except requests.JSONDecodeError as error:
            raise HTTPResponseParsingError(error)

        try:
            price = data['data'][crypto_name][0]['quote']['USD']['price']
            if price:
                return round(price, 2)
            return price
        except (KeyError, IndexError):
            return None
    else:
        return None
