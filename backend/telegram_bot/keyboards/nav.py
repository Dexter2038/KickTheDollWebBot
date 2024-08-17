from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(element: str, page: int, count: int,
                 data: List[int]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for datum in data:
        keyboard.add(
            InlineKeyboardButton(text=datum,
                                 callback_data=f"{element[:-1]}_{datum}"))
    keyboard.add(
        InlineKeyboardButton(
            text="⬅️", callback_data=f"{element}_{0 if page < 1 else page-1}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
        InlineKeyboardButton(
            text="🏠", callback_data=f"{element}_{min(page+1, count//10)}"))
    keyboard.adjust(5, 5, 3)
    return keyboard.as_markup()


def home_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🏠", callback_data="Main"))
    return keyboard.as_markup()