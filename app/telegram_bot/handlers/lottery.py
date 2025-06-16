from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.database import db
from app.telegram_bot.states import States
from app.telegram_bot.keyboards import (
    get_nav_keyboard,
    get_lottery_keyboard,
    get_create_lottery_keyboard,
    get_manage_lottery_keyboard,
    get_home_keyboard,
    get_sure_close_keyboard,
)
from app.lottery import (
    is_current_lottery,
    create_lottery,
    close_lottery,
    change_date_lottery,
)
from ..keyboards import (
    get_main_keyboard,
    get_sure_change_lottery_keyboard,
    get_sure_create_lottery_keyboard,
)

router = Router(name=__name__)

batch_size = 10


@router.callback_query(F.data == "Lottery")
async def history_main(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Всего внесено: {await db.get_sum_lottery_transactions()}$. Выберите действие:",
        reply_markup=get_lottery_keyboard(),
    )


@router.callback_query(F.data == "ManageLottery")
async def manage_lottery(callback: CallbackQuery):
    if is_current_lottery():
        await callback.message.edit_text(
            "Управление розыгрышем", reply_markup=get_manage_lottery_keyboard()
        )
        return
    await callback.message.edit_text(
        "Активного розыгрыша нет", reply_markup=get_create_lottery_keyboard()
    )


@router.callback_query(F.data == "CreateLottery")
async def create_lottery_suggest(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите дату и время окончания розыгрыша в формате: {день:месяц:год.час:минута:секунда}. Пример: 30:09:2024.10:20:00",
        reply_markup=get_home_keyboard(),
    )
    await state.set_state(States.CreateLottery)


@router.message(States.CreateLottery)
async def create_lottery_check(message: Message, state: FSMContext):
    try:
        lottery_date = message.text.split(".")
        if len(lottery_date) != 2:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        date = lottery_date[0].split(":")
        time = lottery_date[1].split(":")
        if len(date) != 3 or len(time) != 3:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        day, month, year = map(int, date)
        hour, minute, second = map(int, time)
        date_time = datetime(year, month, day, hour, minute, second)
        now = datetime.utcnow()
        if date_time < now:
            await message.answer(
                f"Дата не может быть раньше, чем сейчас. пример: 30:09:2024.10:20:00. Сейчас: {now.strftime('%d:%m:%Y.%H:%M:%S')}"
            )
            return
    except ValueError:
        await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
        return
    await state.clear()
    await message.answer(
        f"Вы выбрали: {message.text} по часовому поясу UTC (+0)",
        reply_markup=get_sure_create_lottery_keyboard(message.text),
    )


@router.callback_query(F.data.startswith("CreateLottery_"))
async def move_lottery(callback: CallbackQuery, state: FSMContext):
    _, date = callback.data.split("_")
    if create_lottery(date):
        await callback.message.edit_text(
            text="Вы успешно изменили дату розыгрыша.", reply_markup=get_home_keyboard()
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )


@router.callback_query(F.data == "ChangeLotteryDate")
async def change_lottery_date_suggest(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите дату и время окончания розыгрыша в формате: {день:месяц:год.час:минута:секунда}. Пример: 30:09:2024.10:20:00",
        reply_markup=get_home_keyboard(),
    )
    await state.set_state(States.ChangeLotteryDate)


@router.message(States.ChangeLotteryDate)
async def change_lottery_date_check(message: Message, state: FSMContext):
    try:
        lottery_date = message.text.split(".")
        if len(lottery_date) != 2:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        date = lottery_date[0].split(":")
        time = lottery_date[1].split(":")
        if len(date) != 3 or len(time) != 3:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        day, month, year = map(int, date)
        hour, minute, second = map(int, time)
        date_time = datetime(year, month, day, hour, minute, second)
        now = datetime.utcnow()
        if date_time < now:
            await message.answer(
                f"Дата не может быть раньше, чем сейчас. пример: 30:09:2024.10:20:00. Сейчас: {now.strftime('%d:%m:%Y.%H:%M:%S')}"
            )
            return
    except ValueError:
        await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
        return
    await state.clear()
    await message.answer(
        f"Вы выбрали: {message.text} по часовому поясу UTC (+0)",
        reply_markup=get_sure_change_lottery_keyboard(message.text),
    )


@router.callback_query(F.data.startswith("ChangeLotteryDate_"))
async def move_lottery(callback: CallbackQuery, state: FSMContext):
    _, date = callback.data.split("_")
    if change_date_lottery(date):
        await callback.message.edit_text(
            text="Вы успешно изменили дату розыгрыша.", reply_markup=get_home_keyboard()
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )


@router.callback_query(F.data == "CloseLottery")
async def close_lottery_suggest(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Вы точно хотите закрыть розыгрыш прям сейчас?",
        reply_markup=get_sure_close_keyboard(),
    )


@router.callback_query(F.data == "SureCloseLottery")
async def sure_close_lottery(callback: CallbackQuery, state: FSMContext):
    if close_lottery():
        await callback.message.edit_text(
            text="Вы успешно завершили розыгрыш. Награды начислены.",
            reply_markup=get_home_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )


@router.callback_query(F.data.startswith("Lottery_"))
async def history(callback: CallbackQuery, state: FSMContext, bot: Bot):
    _, page_str = callback.data.split("_")
    page = int(page_str)
    count_transactions = await db.get_count_lottery_transactions()
    if page < 0:
        await bot.answer_callback_query(callback.id, "Назад некуда")
        return
    if (start := page * batch_size + 1) > count_transactions:
        await bot.answer_callback_query(callback.id, "Дальше некуда")
        return
    transactions = await db.get_lottery_transactions(page)
    end = min(start + 9, count_transactions)
    answer = f"Транзакции {start}-{end} из {count_transactions}\n\n"
    data = list()
    for idx, transaction in enumerate(transactions, start=1):
        data.append(transaction.id)
        answer += f"{idx}.{'Подтверждено' if transaction.confirmed_at else 'Не подтверждено'}.[{transaction.created_at}].Пользователь ID:{transaction.telegram_id}.{transaction.amount}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер транзакции на этой странице)"
    await state.set_state(States.LotteryHistory)
    await callback.message.edit_text(
        answer, reply_markup=get_nav_keyboard("Lottery", page, count_transactions, data)
    )


@router.message(States.LotteryHistory)
async def search_history(message: Message, state: FSMContext):
    if message.text.isdigit():
        page = int(message.text)
        if page < 0:
            await message.answer("Номер транзакции не может быть ниже нуля.")
            return
    else:
        await message.answer(text="Сообщение состоит не только из цифр. Введите число")
        return
    count_transactions = await db.get_count_lottery_transactions()
    transactions = await db.get_lottery_transactions(page := page // 10)
    start = page * batch_size + 1
    end = min(start + 9, count_transactions)
    answer = f"Транзакции {start}-{end} из {count_transactions}\n\n"
    data = list()
    for idx, transaction in enumerate(transactions, start=1):
        data.append(transaction.id)
        answer += f"{idx}.{'Подтверждено' if transaction.confirmed_at else 'Не подтверждено'}.[{transaction.created_at}].Пользователь ID:{transaction.telegram_id}.{transaction.amount}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер транзакции на этой странице)"
    await state.set_state(States.LotteryHistory)
    await message.answer(
        answer, reply_markup=get_nav_keyboard("Lottery", page, count_transactions, data)
    )


@router.message()
async def main_panel(message: Message):
    """
    This handler is an entry point for the bot. It shows the main panel with all the available sections.

    :param message: The message that triggered this handler
    """
    # Send the message with the keyboard
    await message.answer("Главное меню", reply_markup=get_main_keyboard())

