from aiogram import F, Router, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (orm_add_subscription, orm_add_subscription_max,
                                orm_add_subscription_min,
                                orm_delete_subscription,
                                orm_get_user_subscription,
                                orm_get_user_subscriptions,
                                orm_update_subscription)
from keyboards import reply
from keyboards.inline import get_callback_btns

from .utils import get_crypto_price, get_float_price, validate_price

user_subscription_router = Router()


# FSM
class AddSubscription(StatesGroup):

    crypto = State()
    min_val = State()
    max_val = State()

    sub_for_change = None


@user_subscription_router.message(Command('subscribe'))
@user_subscription_router.message(
    F.text.strip().lower() == 'подписка на крипту')
async def subscribe_features(message: types.Message):
    await message.answer(
        'Что хотите сделать?',
        reply_markup=reply.subscription_kb.as_markup(resize_keyboard=True))


@user_subscription_router.message(F.text == 'Проверить подписку')
async def check_subscription(message: types.Message, session: AsyncSession):
    subscriptions = await orm_get_user_subscriptions(session, message)
    if len(subscriptions) == 0:
        await message.answer('У вас нет активных подписок.\n'
                             'Это легко исправить! :)')
        return
    await message.answer("Вот ваши подписки:")
    for sub in subscriptions:
        if sub.min_val and sub.max_val:
            await message.answer(f"{sub.crypto}\n"
                                 f'Верхняя цена в USD: $'
                                 f'{get_float_price(sub.max_val)}\n'
                                 f'Нижняя цена в USD: $'
                                 f'{get_float_price(sub.min_val)}',
                                 reply_markup=get_callback_btns(
                                     btns={
                                         "Отписаться": f"delete_{sub.id}",
                                         "Изменить": f"change_{sub.id}",
                                     }))
        elif sub.max_val:
            await message.answer(f"{sub.crypto}\n"
                                 f'Верхняя цена в USD: $'
                                 f'{get_float_price(sub.max_val)}',
                                 reply_markup=get_callback_btns(
                                     btns={
                                         "Отписаться": f"delete_{sub.id}",
                                         "Изменить": f"change_{sub.id}",
                                     }))
        else:
            await message.answer(f"{sub.crypto}\n"
                                 f'Нижняя цена в USD: $'
                                 f'{get_float_price(sub.min_val)}',
                                 reply_markup=get_callback_btns(
                                     btns={
                                         "Отписаться": f"delete_{sub.id}",
                                         "Изменить": f"change_{sub.id}",
                                     }))


@user_subscription_router.callback_query(StateFilter(None),
                                         F.data.startswith("change_"))
async def change_subscription(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    sub_id = callback.data.split("_")[-1]

    sub_for_change = await orm_get_user_subscription(session, int(sub_id))

    crypto_name = sub_for_change.crypto

    await state.set_state(AddSubscription.crypto)
    await state.update_data(crypto=crypto_name)

    AddSubscription.sub_for_change = sub_for_change
    await callback.answer()
    if sub_for_change.min_val:
        await callback.message.answer(
            f"Введите нижнюю стоимость {sub_for_change.crypto} в USD:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddSubscription.min_val)
    else:
        await callback.message.answer(
            f"Введите верхнюю стоимость {sub_for_change.crypto} в USD:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AddSubscription.max_val)


@user_subscription_router.callback_query(F.data.startswith("delete_"))
async def delete_subscription(callback: types.CallbackQuery,
                              session: AsyncSession):
    sub_id = callback.data.split("_")[-1]
    await orm_delete_subscription(session, int(sub_id))

    await callback.answer()
    await callback.message.answer('Вы отписались!')


@user_subscription_router.message(
        StateFilter(None), F.text.strip().lower() == 'подписаться на крипту')
async def subscribe(message: types.Message, state: FSMContext):
    await message.answer(
        'Введите короткое название криптовалюты, на которую хотите'
        ' подписаться, или выберите из представленных:',
        reply_markup=reply.crypto_kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(AddSubscription.crypto)


@user_subscription_router.message(
        StateFilter("*"), Command("cancel"))
@user_subscription_router.message(
    StateFilter("*"), or_f(F.text.casefold() == "отмена",
                           F.text.casefold() == "cancel"))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddSubscription.sub_for_change:
        AddSubscription.sub_for_change = None
    await state.clear()
    await message.answer(
        'Действия отменены.',
        reply_markup=reply.subscription_kb.as_markup(resize_keyboard=True))


@user_subscription_router.message(
        or_f(AddSubscription.max_val, AddSubscription.min_val),
        F.text.casefold() == "закончить")
async def end_sub_handler(
    message: types.Message, state: FSMContext, session: AsyncSession
) -> None:

    data = await state.get_data()
    state_ = await state.get_state()
    if state_ == AddSubscription.min_val:
        try:
            if AddSubscription.sub_for_change:
                await orm_update_subscription(
                    session, AddSubscription.sub_for_change.id, data)
            else:
                await orm_add_subscription_min(session, data, message)
        except Exception as err:
            await message.answer(f'Error:\n'
                                 f'{err}')
    else:
        try:
            if AddSubscription.sub_for_change:
                await orm_update_subscription(
                    session, AddSubscription.sub_for_change.id, data)
            else:
                await orm_add_subscription_max(session, data, message)
        except Exception as err:
            await message.answer(f'Error:\n'
                                 f'{err}')

    await state.clear()
    AddSubscription.sub_for_change = None
    await message.answer(
        'Хорошо, закончим на этом!\n'
        'Вы подписались!',
        reply_markup=reply.subscription_kb.as_markup(resize_keyboard=True))


@user_subscription_router.message(AddSubscription.max_val, F.text == "MIN")
@user_subscription_router.message(AddSubscription.crypto, F.text == "MIN")
async def add_min_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    crypto_name = data['crypto']
    await message.answer(
        f"Введите нижнюю стоимость {crypto_name} в USD:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscription.min_val)


@user_subscription_router.message(AddSubscription.min_val, F.text == "MAX")
@user_subscription_router.message(
    AddSubscription.crypto or AddSubscription.min_val, F.text == "MAX")
async def add_max_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    crypto_name = data['crypto']
    await message.answer(
        f"Введите верхнюю стоимость {crypto_name} в USD:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscription.max_val)


@user_subscription_router.message(AddSubscription.crypto, F.text)
async def add_crypto_name(message: types.Message,
                          state: FSMContext,
                          session: AsyncSession):
    crypto_name = message.text.strip().upper()
    if len(crypto_name) > 7:
        await message.reply(
            'Слишком длинное название.\n'
            'Введите короткое имя криптовалюты вида BTC или SOL:')
        return
    subscriptions = await orm_get_user_subscriptions(session, message)
    for sub in subscriptions:
        if sub.crypto == crypto_name:
            await message.answer(
                'Вы уже подписаны на эту криптовалюту!\n'
                'Проверьте свои подписки.',
                reply_markup=reply.subscription_kb.as_markup(
                    resize_keyboard=True))
            await state.clear()
            return

    price = get_crypto_price(crypto_name)
    if not price:
        await message.reply(
            f"Не удалось получить информацию о стоимости {crypto_name}. "
            f"Проверьте правильность названия и попробуйте снова.")
        return

    await state.update_data(crypto=crypto_name)
    await message.answer(
        f'Стоимость {crypto_name} в данный момент: ${price}.\n'
        f'\n'
        f'На какую цену хотите подписаться: MIN или MAX?',
        reply_markup=reply.value_kb
    )


@user_subscription_router.message(AddSubscription.min_val, F.text)
async def save_min_price(message: types.Message, state: FSMContext,
                         session: AsyncSession):

    validation = await validate_price(message)
    if not validation:
        return

    await state.update_data(min_val=message.text)
    data = await state.get_data()
    min_price = data['min_val']
    crypto_name = data['crypto']

    try:
        max_price = data['max_val']
        if min_price >= max_price:
            await message.answer(
                f'MIN стоимость должна быть меньше MAX стоимости!\n'
                f'Ваша MAX стоимость: ${max_price}.\n'
                f'Введите корректное значение цены:')
            return
    except KeyError:
        pass
    await message.answer(
        f"Вы подписались на стоимость {crypto_name} в USD: ${min_price}."
    )

    try:
        data['max_val']
    except KeyError:
        await message.answer(
            f"Хотите подписаться на MAX стоимость {crypto_name}?\n"
            f"Если хотите продолжить, нажмите <code>MAX</code>.",
            parse_mode=ParseMode.HTML,
            reply_markup=reply.plus_max_price_kb
        )
        return

    try:
        if AddSubscription.sub_for_change:
            await orm_update_subscription(session,
                                          AddSubscription.sub_for_change.id,
                                          data)
        else:
            await orm_add_subscription(session, data, message)
    except Exception as error:
        await message.answer(
            f"Error:\n"
            f"{error}"
        )
    AddSubscription.sub_for_change = None
    await state.clear()


@user_subscription_router.message(AddSubscription.max_val, F.text)
async def save_max_price(message: types.Message,
                         state: FSMContext,
                         session: AsyncSession):

    validation = await validate_price(message)
    if not validation:
        return

    await state.update_data(max_val=message.text)
    data = await state.get_data()
    max_price = data['max_val']
    crypto_name = data['crypto']

    try:
        min_price = data['min_val']
        if max_price < min_price:
            await message.answer(
                f'MAX стоимость должна быть больше MIN стоимости!\n'
                f'Ваша MIN стоимость: ${min_price}.\n'
                f'Введите корректное значение цены:')
            return
    except KeyError:
        pass
    await message.answer(
        f"Вы подписались на стоимость {crypto_name} в USD: ${max_price}."
    )

    try:
        data['min_val']
    except KeyError:
        await message.answer(
            f"Хотите подписаться на MIN стоимость {crypto_name}?\n"
            f"Если хотите продолжить, нажмите <code>MIN</code>.",
            parse_mode=ParseMode.HTML,
            reply_markup=reply.plus_min_price_kb
        )
        return

    try:
        if AddSubscription.sub_for_change:
            await orm_update_subscription(session,
                                          AddSubscription.sub_for_change.id,
                                          data)
        else:
            await orm_add_subscription(session, data, message)
    except Exception as error:
        await message.answer(
            f"Error:\n"
            f"{error}"
        )
    AddSubscription.sub_for_change = None
    await state.clear()
