from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(text="Управлять лотереей",
                             callback_data="ManageLottery"))
    inline_kb.row(
        InlineKeyboardButton(text="Просмотр транзакций по лотерее",
                             callback_data="Lottery_0"))
    inline_kb.row(InlineKeyboardButton(text="🏠", callback_data="Main"), )
    return inline_kb.as_markup()


def create_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Начать новый розыгрыш",
                             callback_data="CreateLottery"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def manage_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Изменить дату окончания",
                             callback_data="ChangeLotteryDate"),
        InlineKeyboardButton(text="Завершить розыгрыш",
                             callback_data="CloseLottery"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def sure_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data="SureCloseLottery"),
        InlineKeyboardButton(text="Нет", callback_data="Lottery"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()
def create_lottery_keyboard(date: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Начать новый розыгрыш",
                             callback_data=f"CreateLottery_{date}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()

def change_lottery_keyboard(date: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="Изменить дату окончания",
                             callback_data=f"ChangeLotteryDate_{date}"),
        InlineKeyboardButton(text="🏠", callback_data="Main"),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()