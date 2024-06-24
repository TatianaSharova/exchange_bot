from aiogram.types import BotCommand

bot_cmds = [
    BotCommand(command='subscribe', description='Подписка на крипту'),
    BotCommand(command='check_price',
               description='Посмотреть стоимость криптовалют'),
    BotCommand(command='help', description='Что может этот бот?'),
    BotCommand(command='cancel', description='Отменить действие')
]
