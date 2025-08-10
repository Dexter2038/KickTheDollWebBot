from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from backend.db.actions import Actions
from backend.db.session import AsyncSession, get_session
from backend.domain.games import LotteryBetRequest

router = APIRouter(prefix="/lottery", tags=["lottery"])


@router.post("/topwinners", response_class=JSONResponse)
async def get_top_lottery_winners(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    winners = await Actions(session).get_top_winners()
    return JSONResponse(
        {
            "msg": "Топ победители лотереи получены успешно",
            "winners": winners,
        }
    )


@router.post("/deposit", response_class=JSONResponse)
async def make_lottery_deposit(
    request: Request,
    data: LotteryBetRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    await Actions(session).make_deposit(request.state.user_id, data.reward, data.bet)
    return JSONResponse({"msg": "Ставка успешно принята"})


@router.post("/", response_class=JSONResponse)
async def get_lottery(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    end_time, amount = await Actions(session).get_current_lottery()
    return JSONResponse(
        {
            "msg": "Лотерея успешно получена",
            "lottery": amount,
            "time": end_time,
        }
    )
