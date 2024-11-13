import os

import aiohttp
import requests
from aiogram import types
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from exceptions import HTTPResponseParsingError

load_dotenv()

COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = os.getenv('COINMARKETCAP_URL')


async def get_float_price(price):
    '''
    Принимает float число и возвращает округленное до 3 знаков после запятой
    float число, если оно больше 0.001.
    В другом случае возвращает строку, состоящую из float числа
    с 10 знаками после запятой, чтобы пользователь не выводилось число вида:
    1e-10.
    '''
    if price and price >= 0.001:
        return round(price, 3)
    if price and price < 0.001:
        return f'{price:.10f}'
    if price and price < 10**(-10):
        return f'{price:.15f}'
    return None


async def get_crypto_price(crypto_name: str) -> float:
    '''
    Обращается к API CoinMarket и получает инф-цию
    о стоимости криптовалюты в USD.
    '''
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
    }
    params = {
        'symbol': crypto_name,
        'convert': 'USD'
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(COINMARKETCAP_URL,
                                   headers=headers,
                                   params=params) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                    except requests.JSONDecodeError as error:
                        raise HTTPResponseParsingError(error)
                else:
                    return None
        except (ConnectionError, Timeout, TooManyRedirects) as error:
            raise HTTPResponseParsingError(error)

        try:
            price = data['data'][crypto_name][0]['quote']['USD']['price']
            return await get_float_price(price)
        except (KeyError, IndexError):
            return None


async def validate_price(message: types.Message) -> bool:
    '''Проверка вводимой стоимости на адекватность.'''
    try:
        float(message.text)
    except ValueError:
        await message.answer(
            'Введите корректное значение цены без пробелов и запятых.\n'
            '\n'
            'Если число меньше 1, оно должно записываться через точку.\n'
            'Например: 0.1'
            )
        return False

    if float(message.text) <= 0:
        await message.answer(
            'Цена должна быть больше 0!\n'
            'Введите корректное значение цены:'
        )
        return False
    if float(message.text) > 10**10:
        await message.answer(
            'У вас очень оптимистичный прогноз :)\n'
            'Но боюсь, ждать придется очень долго,'
            ' введите цену поменьше:'
        )
        return False
    return True
