# **Crypto telegram bot**

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/)

Телеграм бот с trashhold системой, который может предоставить информацию о стоимости выбранной криптовалюты в USD и оформить подписку на стоимость криптовалют.

## Возможности бота:
1. Проверить курс любой криптовалюты:  
Напишите боту короткое название криптовалюты, например BTC или ETH, и вам придет ответ с её стоимостью на данный момент.  

2. Отправлять уведомления:  
Установите минимальную(MIN) и/или максимальную(MAX) цену для криптовалюты.
Бот пришлёт сообщение, когда цена станет ниже или выше заданного вами значения.  

Пример:
Хотите узнать, когда Bitcoin станет дешевле $60,000 или дороже $70,000? Установите эти значения, и бот сообщит вам, когда это произойдет.


### Локальный запуск бота:

**_Склонировать репозиторий к себе_**
```
git@github.com:TatianaSharova/exchange_bot.git
```
**_В директории проекта создать файл .env и заполнить своими данными:_**
```
TELEGRAM_BOT_TOKEN         - токен вашего телеграм бота
COIN_MARKET_TOKEN          - токеy от API криптовалютной биржи CoinMarket
DB_LITE                    - sqlite+aiosqlite:///bot_base.db
COINMARKETCAP_URL          - https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest
```
**_Создать и активировать виртуальное окружение:_**

Для Linux/macOS:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Для Windows:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
**_Установить зависимости из файла requirements.txt:_**
```
pip install -r requirements.txt
```
**_Запустить бот:_**
```
python bot.py
```

### Автор
Татьяна Шарова

