from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from keyboards import reply
from aiogram.enums.parse_mode import ParseMode

from .utils import get_crypto_price

user_canal_router = Router()


@user_canal_router.message(CommandStart())
async def send_welcome(message: types.Message) -> types.Message:
    await message.answer(
        'Теперь я буду помогать тебе отслеживать стоимость криптовалют в USD!\n'
        '\n'
        'Расскажу немного подробнее о том, что я могу делать:\n'
        '\n'
        '1. <b>Проверять курс</b>:\n'
        'Скажите мне название криптовалюты, и я покажу ее текущую стоимость.\n'
        '\n'
        '2. <b>Отправлять уведомления</b>:\n'
        '    - Установите минимальную и/или максимальную цену криптовалюты.\n'
        '    - Я пришлю сообщение, когда цена станет ниже или выше заданного '
        'вами значения.\n'
        '\n'
        '<i>Пример</i>:\n'
        'Хотите узнать, когда Bitcoin станет дешевле $60,000 или дороже $70,000?\n'
        'Установите эти значения, и я сообщу вам, когда это произойдет.\n',
        parse_mode=ParseMode.HTML
        )

    await message.answer(
        'Чтобы начать, выберите в меню интересующие вас функции '
        'или нажмите на всплывшие кнопки:\n'
        '\n'
        'Для просмотра стоимости криптовалют нажмите на кнопку: \n'
        '<code>Криптовалюты</code>\n'
        '\n'
        'Для оформления подписки на стоимость криптовалют'
        'нажмите на кнопку: \n'
        '<code>Подписка на крипту</code>\n',
        parse_mode=ParseMode.HTML,
        reply_markup=reply.help_kb)


@user_canal_router.message(Command('check_price'))
@user_canal_router.message(F.text.lower() == 'криптовалюты')
async def offer_famous_crypto(message: types.Message) -> types.Message:
    await message.reply(
        'Выберите необходимую криптовалюту.\n'
        'Если нужной криптовалюты нет в списке, '
        'отправь боту сообщение с коротким названием криптовалюты, '
        'например, BTC или USDT.'
        )

    await message.answer(
        'Выберите криптовалюту:',
        reply_markup=reply.crypto_kb.as_markup(resize_keyboard=True),
    )


@user_canal_router.message(Command('help'))
@user_canal_router.message(F.text.lower() == 'помощь')
async def get_help(message: types.Message) -> types.Message:
    await message.answer(
        'Я могу:\n'
        '1. Посмотреть стоимость выбранной крипты в USD.\n'
        'Для этого нажми кнопку:\n'
        '<code>Криптовалюты</code>\n'
        '\n'
        '2. Начать отслеживать курс отдельных криптовалют, '
        'присылая уведомления, когда курс достигает выбранных вами значений.\n'
        'Вы можете подписаться на 2 заданных вами значения: MIN и MAX.\n'
        '\n'
        'Если стоимость криптовалюты станет равна или больше MAX: '
        'я пришлю уведомление.\n'
        'Если стоимость криптовалюты станет равна или меньше MIN: '
        'я пришлю уведомление.\n'
        '\n'
        'Чтобы оформить подписку и управлять ей, '
        'нажми на кнопку:\n'
        '<code>Подписка на крипту</code>\n',
        parse_mode=ParseMode.HTML,
        )

    await message.answer('Выберите:', reply_markup=reply.help_kb)


@user_canal_router.message(F.text)
async def send_crypto_price(message: types.Message) -> types.Message:
    crypto_name = message.text.strip().upper()
    if len(crypto_name) > 7:
        await message.reply(
            'Слишком длинное название. Проверьте правильность названия '
            'и попробуйте снова.')
        return

    price = get_crypto_price(crypto_name)

    if price:
        await message.reply(f'Стоимость {crypto_name} в USD: ${price}')
    else:
        await message.reply(
            f'Не удалось получить информацию о стоимости {crypto_name}. '
            f'Проверьте правильность названия и попробуйте снова.')
