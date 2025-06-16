from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.database import db
from app.telegram_bot.states import States
from app.telegram_bot.keyboards import (
    get_nav_keyboard,
    get_balance_keyboard,
    get_home_keyboard,
    get_money_keyboard,
)

router = Router(name=__name__)

batch_size = 10


@router.callback_query(F.data.startswith("Balances_"))
async def balances(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, page_str = callback.data.split("_")
    page = int(page_str)
    count_balances = await db.get_count_users()
    if page < 0:
        await bot.answer_callback_query(callback.id, "Назад некуда")
        return
    if (start := page * batch_size + 1) > count_balances:
        await bot.answer_callback_query(callback.id, "Дальше некуда")
        return
    balances = await db.get_users(page)
    end = min(start + 9, count_balances)
    answer = f"Балансы {start}-{end} из {count_balances}\n\n"
    data = list()
    for idx, balance in enumerate(balances, start=1):
        data.append(balance.telegram_id)
        answer += f"{idx}.ID Владельца:{balance.telegram_id}. Монет:{balance.money_balance}.\n"
    answer += (
        "\n(если вам нужна конкретная страница, введите номер баланса на этой странице)"
    )
    await state.set_state(States.Balances)
    await callback.message.edit_text(
        answer, reply_markup=get_nav_keyboard("Balances", page, count_balances, data)
    )


@router.message(States.Balances)
async def search_balances(message: Message, state: FSMContext):
    if message.text.isdigit():
        page = int(message.text)
        if page < 0:
            await message.answer(text="Номер баланса не может быть ниже нуля.")
            return
    else:
        await message.answer(text="Сообщение состоит не только из цифр. Введите число")
        return
    count_balances = await db.get_count_users()
    balances = await db.get_users(page := page // 10)
    start = page * batch_size + 1
    end = min(start + 9, count_balances)
    answer = f"Балансы {start}-{end} из {count_balances}\n\n"
    data = list()
    for idx, balance in enumerate(balances, start=1):
        data.append(balance.telegram_id)
        answer += (
            f"ID ТГ Владельца:{balance.telegram_id}. Монет:{balance.money_balance}.\n"
        )
    answer += (
        "\n(если вам нужна конкретная страница, введите номер баланса на этой странице)"
    )
    await state.set_state(States.Balances)
    await message.answer(
        answer, reply_markup=get_nav_keyboard("Balances", page, count_balances, data)
    )


@router.callback_query(F.data.startswith("Balance_"))
async def manage_balance(callback: CallbackQuery):
    _, id = callback.data.split("_")
    balance = await db.get_user(int(id))
    await callback.message.edit_text(
        text=(
            f"ID Владельца баланса: {balance.user_id}\n"
            f"ID Телеграмма владельца баланса: {balance.telegram_id}\n"
            f"Никнейм владельца баланса: {balance.username}\n"
            f"Монетный баланс: {balance.money_balance}"
        ),
        reply_markup=get_balance_keyboard(balance.telegram_id),
    )


@router.callback_query(F.data.startswith("EditMoneyBalance_"))
async def edit_money_balance(callback: CallbackQuery, state: FSMContext):
    _, id = callback.data.split("_")
    await state.set_state(States.EditMoneyBalance)
    await state.set_data({"balance_id": int(id)})
    await callback.message.edit_text(
        text="Введите новую сумму", reply_markup=get_home_keyboard()
    )


@router.message(States.EditMoneyBalance)
async def change_money_balance(message: Message, state: FSMContext):
    data = await state.get_data()
    balance_id = data.get("balance_id")
    if not message.text.isdigit() and "." not in message.text:
        await message.answer(text="Введите число.")
        return
    if "." in message.text:
        money_balance = float(message.text)
    else:
        money_balance = int(message.text)
    await state.clear()
    await message.answer(
        (
            f"Вы точно хотите изменить монетный баланс пользователя с ID Телеграмма {balance_id} на {money_balance:.2f}?"
        ),
        reply_markup=get_money_keyboard(balance_id, money_balance),
    )


@router.callback_query(F.data.startswith("SureEditMoneyBalance_"))
async def change_money_balance_confirm(callback: CallbackQuery, state: FSMContext):
    _, balance_id, money_balance = callback.data.split("_")
    await db.edit_money_balance(int(balance_id), float(money_balance))
    await callback.message.edit_text(
        f"Вы успешно изменили монетный баланс пользователя с ID Телеграмма на {money_balance}",
        reply_markup=get_home_keyboard(),
    )
