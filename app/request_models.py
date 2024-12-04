from pydantic import BaseModel


class DefaultRequest(BaseModel):
    initData: str


class PlayerRequest(DefaultRequest):
    player_id: int

class MoneyRequest(PlayerRequest):
    money: float | int

class LotteryBetRequest(PlayerRequest):
    reward: float | int
    bet: float | int

class TransactionRequest(DefaultRequest):
    amount: float
    transaction_type: int

class CoinBetRequest(DefaultRequest):
    coin_name: str
    player_id: int
    way: bool
    time: int
    bet: float

class AmountRequest(PlayerRequest):
    bet: float

class WalletAmountRequest(DefaultRequest):
    amount: int | float

class FinishedGameRequest(DefaultRequest):
    game_type: int
    amount: float
    first_user_id: int
    second_user_id: int | None


class LeaveRequest(DefaultRequest):
    room_id: str
    player_id: int

class WalletRequest(PlayerRequest):
    wallet_address: str

class RoomRequest(DefaultRequest):
    room_id: str


class CreateUserRequest(DefaultRequest):
    username: str
    telegram_id: int
    wallet_address: str


class CreateRoomRequest(DefaultRequest):
    name: str
    reward: int
    player_id: int


class TurnRequest(DefaultRequest):
    room_id: str
    player_id: int


class GetUpdatesRequest(BaseModel):
    room_id: str
    player_id: int


class JoinRequest(DefaultRequest):
    room_id: str
    player_id: int
