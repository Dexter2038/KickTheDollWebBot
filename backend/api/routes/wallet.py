from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from backend.db.actions import Actions
from backend.db.session import AsyncSession, get_session
from backend.domain.transactions import WalletAmountRequest, WalletRequest
from backend.services.ton import get_ton_balance

wallets = []


router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.post("/wallet/disconnect", response_class=JSONResponse)
async def disconnect_wallet(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    await Actions(session).remove_user_wallet(request.state.user_id)
    return JSONResponse({"msg": "Кошелек успешно отключен"})


@router.post("/wallet/connect", response_class=JSONResponse)
async def connect_wallet(
    request: Request,
    data: WalletRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    await Actions(session).add_user_wallet(request.state.user_id, data.wallet_address)
    return JSONResponse({"msg": "Кошелек успешно подключен"})


@router.post("/wallet/deposit", response_class=JSONResponse)
async def get_wallet_for_deposit(
    request: Request, data: WalletAmountRequest
) -> JSONResponse:
    balances = []
    if wallets:
        for wallet in wallets:
            balances.append(await get_ton_balance(wallet))
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Кошельки не найдены")
    index = balances.index(min(balances))
    return JSONResponse(
        {
            "msg": "Баланс успешно пополнен",
            "wallet": wallets[index],
        }
    )


@router.post("/wallet/get_balance", response_class=JSONResponse)
async def get_wallet_balance(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    if not (player := await Actions(session).get_user(request.state.user_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    wallet = player.wallet_address
    balance = await get_ton_balance(wallet)
    logger.info(f"Баланс пользователя {request.state.user_id} получен: {balance}")
    return JSONResponse({"msg": "Баланс получен", "balance": balance})
