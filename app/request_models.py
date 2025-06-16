from typing import Optional
from pydantic import BaseModel


class MoneyRequest(BaseModel):
    money: float


class LotteryBetRequest(BaseModel):
    reward: float
    bet: float


class TransactionRequest(BaseModel):
    amount: float
    transaction_type: int


class CoinBetRequest(BaseModel):
    coin_name: str
    way: bool
    time: int
    bet: float


class AmountRequest(BaseModel):
    bet: float


class WalletAmountRequest(BaseModel):
    amount: float


class FinishedGameRequest(BaseModel):
    game_type: int
    amount: float
    first_user_id: int
    second_user_id: Optional[int]


class WalletRequest(BaseModel):
    wallet_address: str


class RoomRequest(BaseModel):
    room_id: str


class CreateUserRequest(BaseModel):
    username: str
    telegram_id: int
    wallet_address: str


class CreateRoomRequest(BaseModel):
    name: str
    reward: int
