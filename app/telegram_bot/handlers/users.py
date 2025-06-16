from typing import Annotated
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends
from app.db.actions import Actions
from app.db.session import get_session, AsyncSession
from ..states import States
from ..keyboards import (
    get_nav_keyboard,
    get_sure_clear_keyboard,
    get_user_keyboard,
    get_user_money_keyboard,
    get_home_keyboard,
)

router = Router(name=__name__)

batch_size = 10


@router.callback_query(F.data.startswith("Users_"))
async def users(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, page_str = callback.data.split("_")
    page = int(page_str)
    actions = Actions(session)
    count_users = await actions.get_count_users()
    if page < 0:
        await bot.answer_callback_query(callback.id, "Назад некуда")
        return
    if (start := page * batch_size + 1) > count_users:
        await bot.answer_callback_query(callback.id, "Дальше некуда")
        return
    users = await actions.get_users(page)
    end = min(start + 9, count_users)
    answer = f"Пользователи {start}-{end} из {count_users}\n\n"
    data = list()
    for idx, user in enumerate(users, start=1):
        data.append(user.telegram_id)
        answer += f"{idx}. [{user.telegram_id}] @{user.username}. Монеты: {user.money_balance}. Присоединился {user.joined_at.strftime('%d:%m:%Y.%H:%M:%S')}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер пользователя на этой странице)"
    await state.set_state(States.Users)
    await callback.message.edit_text(
        answer, reply_markup=get_nav_keyboard("Users", page, count_users, data)
    )


@router.message(States.Users)
async def search_users(
    message: Message,
    state: FSMContext,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert message.text, "Пустое сообщение"
    if message.text.isdigit():
        page = int(message.text)
    else:
        await message.answer(text="Сообщение состоит не только из цифр. Введите число")
        return
    actions = Actions(session)
    count_users = await actions.get_count_users()
    users = await actions.get_users(page := page // 10)
    start = page * batch_size + 1
    end = min(start + 9, count_users)
    answer = f"Пользователи {start}-{end} из {count_users}\n\n"
    data = list()
    for idx, user in enumerate(users, start=1):
        data.append(user.telegram_id)
        answer += f"{idx}. [{user.telegram_id}] @{user.username}. Монеты: {user.money_balance}. Присоединился {user.joined_at.strftime('%d:%m:%Y.%H:%M:%S')}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер пользователя на этой странице)"
    await state.set_state(States.Users)
    await message.answer(
        answer, reply_markup=get_nav_keyboard("Users", page, count_users, data)
    )


@router.callback_query(F.data.startswith("User_"))
async def user(
    callback: CallbackQuery,
    state: FSMContext,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            text="ID пользователя состоит не только из цифр"
        )
        return
    id = int(id)
    user = await Actions(session).get_user(id)
    await callback.message.edit_text(
        text=(
            f"ID Владельца: {user.telegram_id}\n"
            f"Никнейм: @{user.username}\n"
            f"Монеты: {user.money_balance}\n"
            f"Присоединился {user.joined_at.strftime('%d:%m:%Y.%H:%M:%S')}\n"
        ),
        reply_markup=get_user_keyboard(id),
    )


@router.callback_query(F.data.startswith("ClearUser_"))
async def clear_user(callback: CallbackQuery, state: FSMContext):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            text="ID пользователя состоит не только из цифр"
        )
        return
    id = int(id)
    await callback.message.edit_text(
        text=(f"Вы действительно хотите очистить пользователя с ID {id}?\n(Да/Нет)"),
        reply_markup=get_sure_clear_keyboard(id),
    )


@router.callback_query(F.data.startswith("SureClearUser_"))
async def sure_clear_user(
    callback: CallbackQuery,
    state: FSMContext,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            text="ID пользователя состоит не только из цифр",
            reply_markup=get_home_keyboard(),
        )
        return
    id = int(id)
    await Actions(session).clear_user(id)
    await callback.message.edit_text(
        text=(f"Пользователь с ID {id} очищен"), reply_markup=get_home_keyboard()
    )


@router.callback_query(F.data.startswith("ChangeMoneyBalance_"))
async def change_money_balance(callback: CallbackQuery, state: FSMContext):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    await state.set_state(States.ChangeMoneyBalance)
    await state.set_data({"balance_id": id})
    await callback.message.edit_text(
        text="Введите новый баланс", reply_markup=get_home_keyboard()
    )


@router.message(States.ChangeMoneyBalance)
async def change_money_balance_ask(message: Message, state: FSMContext):
    assert message.text, "Пустое сообщение"
    id = (await state.get_data())["balance_id"]
    try:
        money_balance = float(message.text)
        await message.answer(
            (
                f"Вы точно хотите изменить монетный баланс пользователя с ID Телеграмма {id} на {money_balance:.2f}?"
            ),
            reply_markup=get_user_money_keyboard(id, money_balance),
        )
    except:
        await message.answer(
            "Сообщение состоит не только из цифр. Введите число",
            reply_markup=get_home_keyboard(),
        )


@router.callback_query(F.data.startswith("SureChangeMoneyBalance_"))
async def sure_change_money_balance(
    callback: CallbackQuery,
    state: FSMContext,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id, balance = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            text="ID пользователя состоит не только из цифр",
            reply_markup=get_home_keyboard(),
        )
        return
    id = int(id)
    balance = float(balance)
    await Actions(session).edit_money_balance(id, balance)
    await callback.message.edit_text(
        text=(
            f"Монетный баланс пользователя с ID Телеграмма {id} изменен на {balance:.2f}"
        ),
        reply_markup=get_home_keyboard(),
    )
