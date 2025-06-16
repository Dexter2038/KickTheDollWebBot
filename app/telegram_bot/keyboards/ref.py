from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(
    referral_id: int, referrer_id: int, referred_id: int
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Удалить рефералку", callback_data=f"CloseReferal_{referral_id}"
        ),
        InlineKeyboardButton(
            text="Просмотреть профиль реферала", callback_data=f"User_{referred_id}"
        ),
        InlineKeyboardButton(
            text="Просмотреть профиль реферера", callback_data=f"User_{referrer_id}"
        ),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def sure_keyboard(id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data=f"SureCloseReferral_{id}"),
        InlineKeyboardButton(text="Нет", callback_data=f"Referral_{id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    return keyboard.as_markup()
