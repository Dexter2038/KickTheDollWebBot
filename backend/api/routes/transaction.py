from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from backend.db.actions import Actions
from backend.db.session import AsyncSession, get_session
from backend.domain.transactions import TransactionRequest

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.post("/transaction", response_class=JSONResponse)
async def create_transaction(
    request: Request,
    data: TransactionRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    amount = data.amount
    transaction_type = data.transaction_type

    if not await Actions(session).create_transaction(
        request.state.user_id, amount, transaction_type
    ):
        logger.error(
            f"Не удалось создать транзакцию с данными: ID: {request.state.user_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка создания транзакции"
        )

    logger.info(
        f"Создана транзакция. ID: {request.state.user_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
    )
    return JSONResponse({"msg": "Транзакция успешно создана"}, status.HTTP_201_CREATED)


@router.post("/transaction/get")
async def get_transactions(
    request: Request, session: Annotated[AsyncSession, Depends(get_session)]
) -> JSONResponse:
    transactions = await Actions(session).get_user_transactions(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Транзакции получены",
            "data": transactions,
        }
    )
