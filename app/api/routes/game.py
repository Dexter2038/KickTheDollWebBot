from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.blackjack import generate_room_id
from app.db.actions import Actions
from app.db.session import AsyncSession, get_session
from app.domain.games import FinishedGameRequest
from app.domain.transactions import AmountRequest, MoneyRequest

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/params/get", response_class=JSONResponse)
async def make_game_params(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    money, *bonus, last_visit = await Actions(session).get_game_params(
        request.state.user_id
    )
    return JSONResponse(
        {
            "msg": "Параметры игры получены успешно",
            "params": {
                "money": money,
                "bonus": 1 if all(bonus) else -1,
                "last_visit": last_visit,
            },
        }
    )


@router.post("/add/money", response_class=JSONResponse)
async def add_money(
    request: Request,
    data: MoneyRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    await Actions(session).add_user_money_balance(request.state.user_id, data.money)
    return JSONResponse({"msg": "Деньги успешно добавлены"})


@router.post("/money", response_class=JSONResponse)
async def invest_game_money(
    request: Request,
    data: AmountRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    logger.info(
        f"Пользователь {request.state.user_id} получил в главное игре: {data.bet}"
    )
    await Actions(session).invest_game_money(request.state.user_id, data.bet)
    return JSONResponse({"msg": "Деньги успешно вложены"})


@router.post("/finish", response_class=JSONResponse)
async def create_finished_game(
    request: Request,
    data: FinishedGameRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    game_type = data.game_type
    amount = data.amount
    first_user_id = request.state.user_id
    second_user_id = data.second_user_id
    _hash = generate_room_id()
    if not await Actions(session).mark_finished_game(
        game_type, amount, first_user_id, second_user_id, _hash
    ):
        logger.error(
            f"Не удалось завершить игру с данными: тип игры {game_type}, сумма {amount}, ID первого игрока {first_user_id}, ID второго игрока {second_user_id}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка завершения игры"
        )

    logger.info(
        f"Игра {game_type} {f'между {first_user_id} и {second_user_id}' if second_user_id else f'от {first_user_id}'} "
        f"завершена. Сумма: {amount}"
    )
    return JSONResponse({"msg": "Игра успешно завершена"}, status.HTTP_201_CREATED)
