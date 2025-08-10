from typing import Optional

from pydantic import BaseModel


class LotteryBetRequest(BaseModel):
    reward: float
    bet: float


class CoinBetRequest(BaseModel):
    coin_name: str
    way: bool
    time: int
    bet: float


class CreateRoomRequest(BaseModel):
    name: str
    reward: int


class RoomRequest(BaseModel):
    room_id: str


class FinishedGameRequest(BaseModel):
    game_type: int
    amount: float
    second_user_id: Optional[int]
