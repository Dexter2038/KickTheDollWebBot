from pydantic import BaseModel


class MoneyRequest(BaseModel):
    money: float


class TransactionRequest(BaseModel):
    amount: float
    transaction_type: int


class AmountRequest(BaseModel):
    bet: float


class WalletAmountRequest(BaseModel):
    amount: float


class WalletRequest(BaseModel):
    wallet_address: str
