from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.database import db
from app.telegram_bot.states import States
from app.telegram_bot.keyboards import (
    get_nav_keyboard,
    get_history_keyboard,
    get_home_keyboard,
)

router = Router(name=__name__)

batch_size = 10


@router.callback_query(F.data.startswith("History_"))
async def history(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, page_str = callback.data.split("_")
    page = int(page_str)
    count_transactions = await db.get_count_transactions()
    if page < 0:
        await bot.answer_callback_query(callback.id, "Назад некуда")
        return
    if (start := page * batch_size + 1) > count_transactions:
        await bot.answer_callback_query(callback.id, "Дальше некуда")
        return
    transactions = await db.get_transactions(page)
    end = min(start + 9, count_transactions)
    answer = f"Транзакции {start}-{end} из {count_transactions}\n\n"
    data = list()
    for idx, transaction in enumerate(transactions, start=1):
        data.append(transaction.transaction_id)
        answer += f"{idx}.{'Подтверждено' if transaction.confirmed_at else 'Не подтверждено'}.[{transaction.created_at}:{'Вывод' if transaction.transaction_type else 'Депозит'}].Пользователь ID:{transaction.telegram_id}.{transaction.amount}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер транзакции на этой странице)"
    await state.set_state(States.History)
    await callback.message.edit_text(
        answer, reply_markup=get_nav_keyboard("History", page, count_transactions, data)
    )


@router.message(States.History)
async def search_history(message: Message, state: FSMContext):
    if message.text.isdigit():
        page = int(message.text)
        if page < 0:
            await message.answer("Номер транзакции не может быть ниже нуля.")
            return
    else:
        await message.answer(text="Сообщение состоит не только из цифр. Введите число")
        return
    count_transactions = await db.get_count_transactions()
    transactions = await db.get_transactions(page := page // 10)
    start = page * batch_size + 1
    end = min(start + 9, count_transactions)
    answer = f"Транзакции {start}-{end} из {count_transactions}\n\n"
    data = list()
    for idx, transaction in enumerate(transactions, start=1):
        data.append(transaction.transaction_id)
        answer += f"{idx}.{'Подтверждено' if transaction.confirmed_at else 'Не подтверждено'}.[{transaction.created_at}:{'Вывод' if transaction.transaction_type else 'Депозит'}].Пользователь ID:{transaction.telegram_id}.{transaction.amount}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер транзакции на этой странице)"
    await state.set_state(States.History)
    await message.answer(
        answer, reply_markup=get_nav_keyboard("History", page, count_transactions, data)
    )


@router.callback_query(F.data.startswith("Histor_"))
async def search_histor(callback: CallbackQuery):
    _, id = callback.data.split("_")
    transaction = await db.get_transaction(int(id))
    await callback.message.edit_text(
        text=f"ID Транзакции: {transaction.transaction_id}\n"
        f"Хэш транзакции: {transaction.transaction_hash}\n"
        f"ID Телеграмма пользователя, совершившего транакцию: {transaction.telegram_id}\n"
        f"Тип транзакции: {'Вывод' if transaction.transaction_type else 'Депозит'}\n"
        f"Сумма: {transaction.amount}\n"
        f"Дата проведения: {transaction.created_at.strftime('%d:%m:%Y.%H:%M:%S')}\n"
        f"Статус: {transaction.confirmed_at and transaction.confirmed_at.strftime('%d:%m:%Y.%H:%M:%S') or 'Не подтверждена'}",
        reply_markup=get_history_keyboard(
            transaction.transaction_id,
            transaction.telegram_id,
            True if transaction.confirmed_at else False,
        ),
    )


@router.callback_query(F.data.startswith("ConfirmTransaction_"))
async def confirm_transaction(callback: CallbackQuery):
    _, id = callback.data.split("_")
    if await db.confirm_transaction(int(id)):
        await callback.message.edit_text(
            text="Транзакция успешно подтверждена. Деньги зачислены на баланс.",
            reply_markup=get_home_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )

