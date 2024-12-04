from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.telegram_bot.keyboards import get_main_keyboard
from app.database import db
from app.utils import RegistrationPredictor
from base64 import b64decode

router = Router(name=__name__)

predictor = RegistrationPredictor()


@router.callback_query(F.data == "Main")
async def callback_main_panel(callback: CallbackQuery):
    """
    This handler is an entry point for the bot. It shows the main panel with all the available sections.

    :param message: The message that triggered this handler
    """
    # Send the message with the keyboard
    await callback.message.edit_text("Главное меню",
                                     reply_markup=get_main_keyboard())


@router.message(Command("/admin"))
async def main_panel(message: Message):
    if not (await db.check_admin(message.from_user.id)):
        return
    """
    This handler is an entry point for the bot. It shows the main panel with all the available sections.

    :param message: The message that triggered this handler
    """
    # Send the message with the keyboard
    await message.answer("Главное меню", reply_markup=get_main_keyboard())


@router.message(Command("start"))
async def start(message: Message, command: Command):
    if command:
        args = command.args
        if args:
            decoded = b64decode(args).decode()
            if not predictor.is_ok_referal(message.from_user.id):
                await message.answer(
                    "Вашему аккаунту менее года, вы не можете стать рефералом")
            if (await db.add_referral(decoded, message.from_user.id)):
                referrer = await db.get_user(decoded)
                await message.answer(
                    f"Вы успешно стали рефералом пользователя {referrer.username}! Чтобы начислять приглашающему бонусы, нужен кошелёк с 30+ транзакциями, на котором баланс > 5$, и провести депозит в сумме на 1000 монет"
                )
            else:
                await message.answer(
                    "Неизвестная ошибка. Перезайдите по ссылке пользователя, который вас пригласил"
                )
    else:
        await message.answer(
            "Чтобы успешно зарегистрироваться, войдите в приложение и привяжите кошелёк с 30+ транзакциями, на котором баланс более 10$. При выполнении условий, вы получите бонус!"
        )

