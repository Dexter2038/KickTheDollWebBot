from pydantic import BaseModel


class MoneyRequest(BaseModel):
    money: float | int


class LotteryBetRequest(BaseModel):
    reward: float | int
    bet: float | int


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
    amount: int | float


class FinishedGameRequest(BaseModel):
    game_type: int
    amount: float
    first_user_id: int
    second_user_id: int | None


class LeaveRequest(BaseModel):
    room_id: str


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


class RoomRequest(BaseModel):
    room_id: str


class RoomRequest(BaseModel):
    room_id: str


class RoomRequest(BaseModel):
    room_id: str
