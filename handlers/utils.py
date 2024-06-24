import os

import requests
from dotenv import load_dotenv
from exceptions import HTTPResponseParsingError
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

load_dotenv()

COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = os.getenv('COINMARKETCAP_URL')


def get_float_price(price):
    '''
    Принимает float число и возвращает округленное до 3 знаков после запятой
    float число, если оно больше 0.001.
    В другом случае возвращает строку, состоящую из float числа 
    с 10 знаками после запятой, чтобы пользователь не выводилось число вида:
    6.42113e-05.
    '''
    if price and price >= 0.001:
        return round(price, 3)
    if price and price < 0.001:
        return f'{price:.10f}'
    return None


def get_crypto_price(crypto_name: str) -> float:
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

    try:
        response = requests.get(COINMARKETCAP_URL,
                                headers=headers,
                                params=params)
    except (ConnectionError, Timeout, TooManyRedirects) as error:
        raise HTTPResponseParsingError(error)

    if response.status_code == 200:
        try:
            data = response.json()
        except requests.JSONDecodeError as error:
            raise HTTPResponseParsingError(error)

        try:
            price = data['data'][crypto_name][0]['quote']['USD']['price']
            return get_float_price(price)
        except (KeyError, IndexError):
            return None
    else:
        return None
