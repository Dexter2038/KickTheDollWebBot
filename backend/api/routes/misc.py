from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from backend.db.actions import Actions
from backend.db.session import AsyncSession, get_session
from backend.domain.transactions import AmountRequest
from backend.services.telegram import get_invitation_link

router = APIRouter(tags=["misc"])


@router.post("/money/check", response_class=JSONResponse)
async def check_money_amount(
    request: Request,
    data: AmountRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    if not (player := await Actions(session).get_user(request.state.user_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    logger.info(f"У пользователя: {player.money_balance}. Запрошено: {data.bet}")
    if player.money_balance < data.bet:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно монет"
        )
    return JSONResponse({"msg": "Монет достаточно"})


@router.post("/reward/get", response_class=JSONResponse)
async def find_out_reward(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await Actions(session).get_referral_reward(request.state.user_id)
    return JSONResponse({"msg": "Награда забрана", "reward": reward or 0})


@router.post("/take-reward", response_class=JSONResponse)
async def take_reward(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await Actions(session).take_referral_reward(request.state.user_id)
    return JSONResponse({"msg": "Награда забрана", "reward": reward})


@router.post("/reward/post", response_class=JSONResponse)
async def get_reward(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await Actions(session).take_referral_reward(request.state.user_id)
    logger.info(f"Пользователь {request.state.user_id} получил награду: {reward}")
    return JSONResponse({"msg": "Награда забрана", "reward": reward})


@router.post("/referral/get", response_class=JSONResponse)
async def get_referral_count(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    """
    Get count of referrals of certain user
    """
    referral_count = await Actions(session).get_referral_count(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Количество рефералов получено",
            "referral_count": referral_count,
        }
    )


@router.post("/invite/link", response_class=JSONResponse)
async def get_invite_link(request: Request) -> JSONResponse:
    """
    Get invitation link for certain user
    """
    invite_link = await get_invitation_link(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Ссылка для приглашения получена",
            "invite_link": invite_link,
        }
    )
