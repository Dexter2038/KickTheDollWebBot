from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.api.jwt import create_refresh_token, create_access_token
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.actions import Actions
from app.db.session import get_session
from app.domain.user import CreateUserRequest

router = APIRouter(prefix="/player", tags=["player"])


@router.post("/login", response_class=JSONResponse)
async def login_player(
    session: Annotated[AsyncSession, Depends(get_session)],
    init_data: str,
    wallet_address: str,
) -> JSONResponse:
    telegram_id = await Actions(session).login_user(init_data, wallet_address)
    if not telegram_id:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    refresh_token = await create_refresh_token(session, telegram_id, timedelta(days=7))
    access_token = await create_access_token(telegram_id, timedelta(days=1))
    if not refresh_token or not access_token:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = JSONResponse({})
    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, secure=True, samesite="strict"
    )
    response.set_cookie(
        "access_token", access_token, httponly=True, secure=True, samesite="strict"
    )
    return response


@router.post("/get", response_class=JSONResponse)
async def get_player_by_id(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    if not (player := await Actions(session).get_user(request.state.user_id)):
        logger.warning(
            f"Была попытка поиска пользователя под id: {request.state.user_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    logger.info(f"Пользователь {request.state.user_id} был взят из базы данных")
    return JSONResponse(
        {
            "msg": "Игрок успешно найден",
            "player": {
                "wallet_address": player.wallet_address,
                "money_balance": player.money_balance,
            },
        }
    )


@router.post("/post", response_class=JSONResponse)
async def create_player(
    data: CreateUserRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    wallet_address = data.wallet_address
    username = data.username
    telegram_id = data.telegram_id
    if not await Actions(session).create_user(
        telegram_id=telegram_id, username=username, wallet_address=wallet_address
    ):
        logger.error(
            f"Не удалось создать игрока с данными: ID: {data.telegram_id}. Никнейм: {data.username}. Адрес кошелька: {data.wallet_address}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка создания игрока"
        )
    logger.info(
        f"Создан пользователь. ID: {data.telegram_id}. Никнейм: {data.username}. Адрес кошелька: {data.wallet_address}"
    )
    return JSONResponse({"msg": "Игрок успешно создан"}, status.HTTP_201_CREATED)
