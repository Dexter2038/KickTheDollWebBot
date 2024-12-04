from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Транзакции", callback_data="History_0"),
        InlineKeyboardButton(text="Пользователи", callback_data="Users_0"),
        InlineKeyboardButton(text="Рефералы", callback_data="Referrals_0"),
        InlineKeyboardButton(text="Балансы", callback_data="Balances_0"),
        InlineKeyboardButton(text="Техническое", callback_data="Tech"),
        InlineKeyboardButton(text="Розыгрыши", callback_data="Lottery"))
    keyboard.adjust(1)
    return keyboard.as_markup()
