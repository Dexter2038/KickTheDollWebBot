from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.tech import is_tech_works

def get_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if is_tech_works():
        keyboard.add(
            InlineKeyboardButton(text="Закончить технические работы", callback_data="EndTechWorks"),
            InlineKeyboardButton(text="Перенести технические работы", callback_data="MoveTechWorks"),
            InlineKeyboardButton(text="🏠", callback_data="Main"),
        )
    else:
        keyboard.add(
            InlineKeyboardButton(text="Закрыть бота на технические работы", callback_data="TechWorks"),
            InlineKeyboardButton(text="🏠", callback_data="Main"),
        )
    keyboard.adjust(1)
    return keyboard.as_markup()


def sure_keyboard(date: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data=f"TechYes_{date}"),
        InlineKeyboardButton(text="Нет", callback_data="TechWorks"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    return keyboard.as_markup()

def sure_close_tech_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data="SureEndTechWorks"),
        InlineKeyboardButton(text="Нет", callback_data="TechWorks"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    return keyboard.as_markup()

def sure_move_tech_keyboard(date: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data=f"SureMoveTechWorks_{date}"),
        InlineKeyboardButton(text="Нет", callback_data="TechWorks"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    return keyboard.as_markup()