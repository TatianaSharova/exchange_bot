from aiogram import F, Router, types
from aiogram.filters import CommandStart
from keyboards import reply
from .utils import get_crypto_price
from aiogram.enums import ParseMode


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
async def offer_famous_crypto(message: types.Message) -> types.Message:
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
async def get_help(message: types.Message) -> types.Message:
    await message.answer(
        "Этот бот может:\n"
        "1. Посмотреть стоимость выбранной крипты в USD.\n"
        "Для этого нажми кнопку <Криптовалюты>.\n"
        "2. Начать отслеживать курс отдельных криптовалют, "
        "присылая уведомления, когда курс достигает выбранных вами значений.\n"
        "Для этого нажми на кнопку <Подписка на крипту>."
        "3. Отменить подписку на криптовалюту.\n"
        "Для этого нажми на кнопку <Отменить подписку>."
        "4. Изменить подписку на криптовалюту.\n"
        "Для этого нажми на кнопку <Изменить подписку>."
        )

    await message.answer(
        "Выберите:",
        reply_markup=reply.help_kb.as_markup(resize_keyboard=True)
    )


@user_canal_router.message(F.text.strip().lower() == "подписка на крипту")
async def follow_crypto(message: types.Message) -> types.Message:
    await message.answer(text=
        "Вы можете подписаться на определенную стоимость криптовалюты в USD, "
        "и когда криптовалюта достигнет этой стоимости или перешагнет этот порог,"
        " мы пришлем вам уведомление.\n"
        "\n"
        "Вы можете подписаться на 2 заданных значения: MIN и MAX.\n"
        "\n"
        "Если стоимость криптовалюты станет равна или больше MAX: "
        "мы пришлем уведомление об этом.\n"
        "Если стоимость криптовалюты станет равна или меньше MIN: "
        "мы пришлем уведомление об этом.\n"
        "\n"
        "Чтобы подписаться на MAX стоимость криптовалюты, отправьте боту сообщение вида:\n"
        "<code>MAX BTC 67000</code>\n"
        "или\n"
        "<code>MAX NOT 0,02</code>\n"
        "\n"
        "Чтобы подписаться на MIN стоимость криптовалюты, отправьте боту сообщение вида:\n"
        "<code>MIN BTC 65000</code>\n"
        "или\n"
        "<code>MIN NOT 0,009</code>",
        parse_mode=ParseMode.HTML
        )


@user_canal_router.message(F.text)
async def send_crypto_price(message: types.Message) -> types.Message:
    crypto_name = message.text.strip().upper()
    if len(crypto_name) > 7:
        await message.reply(
            "Слишком длинное название. Проверьте правильность названия "
            "и попробуйте снова.")
    else:
        price = get_crypto_price(crypto_name)

        if price:
            await message.reply(f"Стоимость {crypto_name} в USD: ${price}")
        else:
            await message.reply(
                f"Не удалось получить информацию о стоимости {crypto_name}. "
                f"Проверьте правильность названия и попробуйте снова.")


@user_canal_router.message(F.text.strip().lower() == "отмена подписки")
async def unfollow_crypto(message: types.Message) -> types.Message:
    await message.answer('Раздел в работе.')


@user_canal_router.message(F.text.strip().lower() == "изменить подписку")
async def unfollow_crypto(message: types.Message) -> types.Message:
    await message.answer('Раздел в работе.')
