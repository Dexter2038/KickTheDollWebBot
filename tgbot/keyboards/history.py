from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(trans_id, user_id, _is_confirmed) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    if not _is_confirmed:
        keyboard.add(
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"ConfirmTransaction_{trans_id}"))
    keyboard.add(
        InlineKeyboardButton(text="Перейти к профилю пользователя",
                             callback_data=f"User_{user_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"))
    keyboard.adjust(1)
    return keyboard.as_markup()
