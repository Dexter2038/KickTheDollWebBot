from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Очистить профиль", callback_data=f"ClearUser_{telegram_id}"
        ),
        InlineKeyboardButton(
            text="Изменить монетный баланс",
            callback_data=f"ChangeMoneyBalance_{telegram_id}",
        ),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def get_clear_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data=f"SureClearUser_{telegram_id}"),
        InlineKeyboardButton(text="Нет", callback_data=f"User_{telegram_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def get_money_balance(telegram_id: int, balance: float) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Да", callback_data=f"SureChangeMoneyBalance_{telegram_id}_{balance}"
        ),
        InlineKeyboardButton(text="Нет", callback_data=f"User_{telegram_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
