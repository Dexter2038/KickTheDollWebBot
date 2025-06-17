from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    telegram_id: int
    wallet_address: str
