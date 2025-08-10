from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from tgbot.keyboards import (
    get_tech_keyboard,
    get_tech_sure_keyboard,
    get_home_keyboard,
    get_close_tech_keyboard as get_sure_close_tech_keyboard,
    get_move_tech_keyboard as get_sure_move_tech_keyboard,
)
from tgbot.states import States

from backend.db.actions import TechActions

from datetime import UTC, datetime

router = Router(name=__name__)


@router.callback_query(F.data == "Tech")
async def tech(callback: CallbackQuery):
    assert callback.message, "Пустое сообщение"
    await callback.message.edit_text(
        "Выберите опцию:", reply_markup=get_tech_keyboard()
    )


@router.callback_query(F.data == "TechWorks")
async def tech_works_enter(callback: CallbackQuery, state: FSMContext):
    assert callback.message, "Пустое сообщение"
    await state.set_state(States.Tech)
    await callback.message.edit_text(
        "Введите время и дату окончания технических работ по часовому поясу UTC(0+) в формате: {день:месяц:год.час:минута:секунда}. Пример: 30:09:2024.10:20:00",
        reply_markup=get_home_keyboard(),
    )


@router.message(States.Tech)
async def tech_works_check(message: Message, state: FSMContext):
    assert message.text, "Пустое сообщение"
    try:
        tech_works_date = message.text.split(".")
        if len(tech_works_date) != 2:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        date = tech_works_date[0].split(":")
        time = tech_works_date[1].split(":")
        if len(date) != 3 or len(time) != 3:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        day, month, year = map(int, date)
        hour, minute, second = map(int, time)
        date_time = datetime(year, month, day, hour, minute, second)
        now = datetime.now(UTC)
        if date_time < now:
            await message.answer(
                f"Дата не может быть раньше, чем сейчас. пример: 30:09:2024.10:20:00. Сейчас: {now.strftime('%d:%m:%Y.%H:%M:%S')}"
            )
    except ValueError:
        await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
        return
    await state.update_data(tech_works_date=message.text)
    await message.answer(
        f"Вы выбрали: {message.text} по часовому поясу UTC (+0)",
        reply_markup=get_tech_sure_keyboard(message.text),
    )


@router.callback_query(F.data.startswith("TechYes_"))
async def tech_works_confirm(callback: CallbackQuery):
    assert callback.data and callback.message, "Пустое сообщение"
    text = callback.data.split("_")[1]
    if TechActions().start_works(text):
        await callback.message.edit_text(
            f"Вы начали технические работы, которые закончатся {text} по часовому поясу 0+",
            reply_markup=get_home_keyboard(),
        )
    else:
        await callback.message.edit_text(
            "Невозможно начать работы.", reply_markup=get_home_keyboard()
        )


@router.callback_query(F.data == "EndTechWorks")
async def tech_works_end(callback: CallbackQuery):
    assert callback.message, "Пустое сообщение"
    await callback.message.edit_text(
        text="Вы точно хотите закончить технические работы прям сейчас?",
        reply_markup=get_sure_close_tech_keyboard(),
    )


@router.callback_query(F.data == "SureEndTechWorks")
async def tech_works_end_confirm(callback: CallbackQuery):
    assert callback.message, "Пустое сообщение"
    if TechActions().end_tech_works():
        await callback.message.edit_text(
            text="Вы успешно закончили технические работы.",
            reply_markup=get_home_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )


@router.callback_query(F.data == "MoveTechWorks")
async def tech_works_move(callback: CallbackQuery, state: FSMContext):
    assert callback.message, "Пустое сообщение"
    await callback.message.edit_text(
        "Введите новую дату и время окончания технических работ в формате: {день:месяц:год.час:минута:секунда}. Пример: 30:09:2024.10:20:00",
        reply_markup=get_home_keyboard(),
    )
    await state.set_state(States.MoveTechWorks)


@router.message(States.MoveTechWorks)
async def tech_works_move_check(message: Message, state: FSMContext):
    assert message.text, "Пустое сообщение"
    try:
        tech_works_date = message.text.split(".")
        if len(tech_works_date) != 2:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        date = tech_works_date[0].split(":")
        time = tech_works_date[1].split(":")
        if len(date) != 3 or len(time) != 3:
            await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
            return
        day, month, year = map(int, date)
        hour, minute, second = map(int, time)
        date_time = datetime(year, month, day, hour, minute, second)
        now = datetime.now(UTC)
        if date_time < now:
            await message.answer(
                f"Дата не может быть раньше, чем сейчас. пример: 30:09:2024.10:20:00. Сейчас: {now.strftime('%d:%m:%Y.%H:%M:%S')}"
            )
            return
    except ValueError:
        await message.answer("Неверный формат. пример: 30:09:2024.10:20:00")
        return
    await message.answer(
        f"Вы выбрали: {message.text} по часовому поясу UTC (+0)",
        reply_markup=get_sure_move_tech_keyboard(message.text),
    )


@router.callback_query(F.data.startswith("SureMoveTechWorks_"))
async def sure_move_tech_works(callback: CallbackQuery, state: FSMContext):
    assert callback.data and callback.message, "Пустое сообщение"
    _, date = callback.data.split("_")
    if TechActions().change_date_tech_works(date):
        await callback.message.edit_text(
            text="Вы успешно изменили дату технических работ.",
            reply_markup=get_home_keyboard(),
        )
    else:
        await callback.message.edit_text(
            text="Произошла ошибка.", reply_markup=get_home_keyboard()
        )
