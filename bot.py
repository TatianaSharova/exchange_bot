import asyncio
import os
import logging
import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
from exceptions import HTTPResponseParsingError

load_dotenv()

API_TOKEN = os.getenv('TEELEGRAM_TOKEN')
COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


logging.basicConfig(level=logging.INFO)


router: Router = Router()
dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=API_TOKEN)


@dp.message(Command("start"))
async def send_welcome(message: types.Message) -> types.Message:
    await message.reply("Привет! Я бот, который может предоставить информацию о стоимости выбранной криптовалюты в USD.\n"
                        "Нажми на кнопку <Криптовалюты>, чтобы перейти к нужной криптовалюте.\n"
                        "Если хочешь ознакомиться со всеми функциями бота, нажми на кнопку <Помощь>.")

    kb = [
        [
            types.KeyboardButton(text="Криптовалюты"),
            types.KeyboardButton(text="Помощь")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True
        #input_field_placeholder=":)"
    )
    await message.answer("Выберите опцию:", reply_markup=keyboard)

@dp.message(F.text.lower() == "криптовалюты")
async def offer_famous_crypto(message: types.Message):
    await message.reply("Выбери необходимую криптовалюту.\n"
                        "Если нужной криптовалюты нет в списке, "
                        "отправь боту сообщение с коротким названием криптовалюты, "
                        "например, BTC или USDT.")

    builder = ReplyKeyboardBuilder()
    crypto_symbols = ['BTC', 'ETH', 'USDT', 'LTC', 'XLM', 'SOL', 'BNB', 'NOT', 'TON']
    for crypto in crypto_symbols:
        builder.add(types.KeyboardButton(text=crypto))
    builder.adjust(3)
    await message.answer(
        "Выберите криптовалюту:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(F.text.lower() == "помощь")
async def get_help(message: types.Message):
    await message.reply("Этот бот может:\n"
                        "1. Посмотреть стоимость выбранной крипты в USD.\n"
                        "Для этого нажми кнопку 'Криптовалюты'.\n"
                        "2. Начать отслеживать курс отдельных криптовалют, "
                        "присылая уведомления, когда курс достигает выбранных вами значений.\n"
                        "Для этого нажми на кнопку 'Подписка на крипту'.")

    builder = ReplyKeyboardBuilder()
    crypto_symbols = ['Криптовалюты','Подписка на крипту']
    for crypto in crypto_symbols:
        builder.add(types.KeyboardButton(text=crypto))
    builder.adjust(2)
    await message.answer(
        "Выберите:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(F.text.strip().lower() == "подписка на крипту")
async def follow_crypto(message: types.Message):
    await message.reply("Раздел пока в работе.")


@router.message(F.text)
async def send_crypto_price(message: types.Message):
    crypto_name = message.text.strip().upper()
    price = get_crypto_price(crypto_name)
    
    if price:
        await message.reply(f"Стоимость {crypto_name} в USD: ${price}")
    else:
        await message.reply(f"Не удалось получить информацию о стоимости {crypto_name}. Проверьте правильность названия криптовалюты и попробуйте снова.")

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
        response = requests.get(COINMARKETCAP_URL, headers=headers, params=params)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        raise Exception(e)                                                           #TODO Exception
    
    if response.status_code == 200:
        try:
            data = response.json()
        except requests.JSONDecodeError as error:
            raise HTTPResponseParsingError(error)

        try:
            price = data['data'][crypto_name][0]['quote']['USD']['price']
            return price
            #return round(price, 2)
        except KeyError:
            return None
    else:
        return None


async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)

    while True:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())





# def check_tokens() -> bool:
#     '''Проверка доступности необходимых переменных окружения.'''
#     logging.info('Проверка доступности переменных окружения.')
#     tokens = [TELEGRAM_BOT_TOKEN, COIN_MARKET_TOKEN]
#     if all(tokens):
#         logging.info('Проверка успешно пройдена.')
#     return all(tokens)


# @router.message(F.text)
# async def speech_to_text(message: Message, bot: Bot) -> Message:
#     await message.reply(text='hi')


# async def main():
#     if not check_tokens():
#         logging.critical('Отсутствуют необходимые переменные окружения.')
#         sys.exit(1)
#     bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)
#     dp: Dispatcher = Dispatcher()
#     dp.include_router(router)
#     await bot.delete_webhook(drop_pending_updates=True)

#     while True:
#         await dp.start_polling(bot)


# if __name__ == "__main__":
#     asyncio.run(main())