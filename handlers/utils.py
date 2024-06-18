import os
from dotenv import load_dotenv
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests
from exceptions import HTTPResponseParsingError

load_dotenv()

COINMARKETCAP_API_KEY = os.getenv('COIN_MARKET_TOKEN')
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'


def get_crypto_price(crypto_name: str) -> float:
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
                return round(price, 3)
            return price
        except (KeyError, IndexError):
            return None
    else:
        return None