from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard(telegram_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Изменить долларовый баланс",
                             callback_data=f"EditDollarBalance_{telegram_id}"),
        InlineKeyboardButton(text="Изменить монетный баланс",
                             callback_data=f"EditMoneyBalance_{telegram_id}"),
        InlineKeyboardButton(text="Перейти к профилю пользователя",
                             callback_data=f"User_{telegram_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def dollar_keyboard(telegram_id: str | int,
                    new_balance: float) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Да",
            callback_data=f"SureEditDollarBalance_{telegram_id}_{new_balance}"
        ),
        InlineKeyboardButton(text="Нет",
                             callback_data=f"Balance_{telegram_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def money_keyboard(telegram_id: str | int,
                   new_balance: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Да",
            callback_data=f"SureEditMoneyBalance_{telegram_id}_{new_balance}"),
        InlineKeyboardButton(text="Нет",
                             callback_data=f"Balance_{telegram_id}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"))
    keyboard.adjust(1)
    return keyboard.as_markup()
