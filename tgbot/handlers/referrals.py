from typing import Annotated
from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends
from backend.db.session import get_session, AsyncSession
from tgbot.states import States
from backend.db.actions import Actions
from tgbot.keyboards import (
    get_nav_keyboard,
    get_ref_keyboard,
    get_home_keyboard,
    get_ref_sure_keyboard,
)

batch_size = 10

router = Router(name=__name__)


@router.callback_query(F.data.startswith("Referrals_"))
async def referrals(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, page_str = callback.data.split("_")
    page = int(page_str)
    actions = Actions(session)
    count_referrals = await actions.get_count_referrals()
    if page < 0:
        await bot.answer_callback_query(callback.id, "Назад некуда")
        return
    if (start := page * batch_size + 1) > count_referrals:
        await bot.answer_callback_query(callback.id, "Дальше некуда")
        return
    referrals = await actions.get_referrals(page)
    end = min(start + 9, count_referrals)
    answer = f"Рефери {start}-{end} из {count_referrals}\n\n"
    data = list()
    for idx, referral in enumerate(referrals, start=1):
        data.append(referral.referral_id)
        answer += f"{idx}.[{referral.referrer_id}-{referral.referred_id}]: Бонус:{referral.bonus}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер реферала на этой странице)"
    await state.set_state(States.Referrals)
    await callback.message.edit_text(
        answer, reply_markup=get_nav_keyboard("Referrals", page, count_referrals, data)
    )


@router.message(States.Referrals)
async def search_referrals(
    message: Message,
    state: FSMContext,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert message.text, "Пустое сообщение"
    if message.text.isdigit():
        page = int(message.text)
    else:
        await message.answer(text="Сообщение состоит не только из цифр. Введите число")
        return
    actions = Actions(session)
    count_referrals = await actions.get_count_referrals()
    referrals = await actions.get_referrals(page := page // 10)
    start = page * batch_size + 1
    end = min(start + 9, count_referrals)
    answer = f"Рефералы {start}-{end} из {count_referrals}\n\n"
    data = list()
    for idx, referral in enumerate(referrals, start=1):
        data.append(referral.referral_id)
        answer += f"{idx}.[{referral.referrer_id}-{referral.referred_id}]: Бонус:{referral.bonus}\n"
    answer += "\n(если вам нужна конкретная страница, введите номер реферала на этой странице)"
    await state.set_state(States.Referrals)
    await message.answer(
        answer, reply_markup=get_nav_keyboard("Referrals", page, count_referrals, data)
    )


@router.callback_query(F.data.startswith("Referral_"))
async def search_referral(
    callback: CallbackQuery,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            "ID должен состоять только из цифр", reply_markup=get_home_keyboard()
        )
        return
    id = int(id)
    referral = await Actions(session).get_referral(id)
    if not referral:
        await callback.message.edit_text(
            "Реферал не найден", reply_markup=get_home_keyboard()
        )
        return
    status = (
        "Успешно"
        if referral.status
        else "Реферал ещё не зарегистрировался"
        if referral.status is None
        else "Реферал ещё не выполнил условия"
    )
    await callback.message.edit_text(
        f"ID Рефералки: {referral.referral_id}\n"
        f"ID Реферала: {referral.referred_id}\n"
        f"ID Реферера (от кого реферал): {referral.referrer_id}\n"
        f"Бонус: {referral.bonus}\n"
        f"Статус: {status}",
        reply_markup=get_ref_keyboard(id, referral.referrer_id, referral.referred_id),
    )


@router.callback_query(F.data.startswith("CloseReferral_"))
async def close_referral_confirm(callback: CallbackQuery):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить рефералку?\nЕё нельзя будет возобновить.\nID рефералки: {id}",
        reply_markup=get_ref_sure_keyboard(id),
    )


@router.callback_query(F.data.startswith("SureCloseReferral_"))
async def close_referral(
    callback: CallbackQuery,
    session: Annotated[AsyncSession, Depends(get_session, use_cache=False)],
):
    assert callback.data and callback.message, "Пустое сообщение"
    _, id = callback.data.split("_")
    if not id.isdigit():
        await callback.message.edit_text(
            "ID должен состоять только из цифр", reply_markup=get_home_keyboard()
        )
        return
    await Actions(session).delete_referral(int(id))
    await callback.message.edit_text(
        f"Рефералка с ID: {id} удалена.", reply_markup=get_home_keyboard()
    )
