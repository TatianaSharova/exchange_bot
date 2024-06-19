from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards import reply
from .utils import get_crypto_price


user_subscription_router = Router()


@user_subscription_router.message(Command("subscribe"))
async def subscribe_features(message: types.Message):
    await message.answer("Что хотите сделать?",
                         reply_markup=reply.subscription_kb.as_markup(resize_keyboard=True))


@user_subscription_router.message(F.text == "Проверить подписку")
async def starring_at_product(message: types.Message):
    await message.answer("Вот ваша подписка")


@user_subscription_router.message(F.text == "Изменить подписку")
async def change_subscription(message: types.Message):
    await message.answer("ОК, вот список товаров")


@user_subscription_router.message(F.text == "Отменить подписку")
async def delete_subscription(message: types.Message):
    await message.answer("Выберите подписку для удаления")


#Код ниже для машины состояний (FSM)

class AddSubscription(StatesGroup):

    crypto = State()
    min_val = State()
    max_val = State()

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }


@user_subscription_router.message(StateFilter(None), F.text.strip().lower() == "подписаться на крипту")
async def subscribe(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите короткое название криптовалюты вида BTC или ETH.", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscription.crypto)


@user_subscription_router.message(StateFilter('*'), Command("отмена"))
@user_subscription_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены.",
                         reply_markup=reply.subscription_kb.as_markup(resize_keyboard=True))


@user_subscription_router.message(AddSubscription.max_val, F.text == "MIN")
@user_subscription_router.message(AddSubscription.crypto, F.text == "MIN")
async def add_min_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    crypto_name = data['crypto']
    await message.answer(
        f"Введите нижнюю стоимость {crypto_name}:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscription.min_val)


@user_subscription_router.message(AddSubscription.min_val, F.text == "MAX")
@user_subscription_router.message(AddSubscription.crypto or AddSubscription.min_val, F.text == "MAX")
async def add_max_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    crypto_name = data['crypto']
    await message.answer(
        f"Введите верхнюю стоимость {crypto_name}:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscription.max_val)


@user_subscription_router.message(AddSubscription.crypto, F.text)
async def add_crypto_name(message: types.Message, state: FSMContext):
    crypto_name = message.text.strip().upper()
    if len(crypto_name) > 7:
        await message.reply(
            "Слишком длинное название. Проверьте правильность названия "
            "и попробуйте снова.")
        return
    
    price = get_crypto_price(crypto_name)
    if not price:
        await message.reply(
            f"Не удалось получить информацию о стоимости {crypto_name}. "
            f"Проверьте правильность названия и попробуйте снова.")
        return

    await state.update_data(crypto=crypto_name)
    await message.answer(
        "На какую цену хотите подписаться: MIN или MAX?",
        reply_markup=reply.value_kb
    )


@user_subscription_router.message(AddSubscription.min_val, F.text)
async def save_min_price(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer("Введите корректное значение цены:")
        return
    
    await state.update_data(min_val=message.text)
    data = await state.get_data()
    min_price = data['min_val']
    crypto_name = data['crypto']
    await message.answer(
        f"Вы подписались на стоимость {crypto_name} в USD: ${min_price}."
    )

    try:
        data['max_val']
        await state.clear()
    except KeyError as error:
        await message.answer(
            f"Хотите подписаться на MAX стоимость {crypto_name}?\n"
            f"Если хотите продолжить, нажмите <MAX>.",
            reply_markup=reply.plus_max_price_kb
        )
        return


@user_subscription_router.message(AddSubscription.max_val, F.text)
async def save_max_price(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer("Введите корректное значение цены:")
        return
    
    await state.update_data(max_val=message.text)
    data = await state.get_data()
    max_price = data['max_val']
    crypto_name = data['crypto']
    await message.answer(
        f"Вы подписались на стоимость {crypto_name} в USD: ${max_price}."
    )

    try:
        data['min_val']
        await state.clear()
    except KeyError as error:
        await message.answer(
            f"Хотите подписаться на MIN стоимость {crypto_name}?\n"
            f"Если хотите продолжить, нажмите <MIN>.",
            reply_markup=reply.plus_min_price_kb
        )
        return
