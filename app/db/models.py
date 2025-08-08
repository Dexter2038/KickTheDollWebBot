from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import BIGINT


class Model(DeclarativeBase):
    pass


class Users(Model):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    username: Mapped[str] = mapped_column(String(30))
    wallet_address: Mapped[str] = mapped_column(
        String(128),
    )
    admin: Mapped[bool] = mapped_column(nullable=True, default=None)
    money_balance: Mapped[float] = mapped_column(default=0)
    last_visit_to_bot: Mapped[datetime] = mapped_column(
        nullable=True, default=datetime.now(UTC) - timedelta(hours=5)
    )
    bonuses_to_bot: Mapped[int] = mapped_column(nullable=True, default=3)
    total_transactions: Mapped[float] = mapped_column(default=0)
    joined_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())


class Wallets(Model):
    __tablename__ = "wallets"

    wallet_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.telegram_id"))
    blockchain: Mapped[str] = mapped_column(String(16), nullable=False)
    address: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(default=0)


class Bets(Model):
    __tablename__ = "bets"

    bet_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.telegram_id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[bool] = mapped_column(default=None, nullable=True)
    way: Mapped[int]
    coin: Mapped[str]
    start_value: Mapped[float]
    supposed_at: Mapped[datetime]


class FinishedGame(Model):
    __tablename__ = "finished_games"

    game_id: Mapped[int] = mapped_column(primary_key=True)
    game_type: Mapped[int] = mapped_column(nullable=False)
    first_user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.telegram_id"))
    second_user_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=True
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    game_hash: Mapped[str] = mapped_column(nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.current_timestamp()
    )


class Referrals(Model):
    __tablename__ = "referrals"

    referral_id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False
    )
    referred_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.telegram_id"), nullable=False
    )
    bonus: Mapped[float] = mapped_column(default=0)
    status: Mapped[bool] = mapped_column(nullable=True, default=None)


class Transactions(Model):
    __tablename__ = "transactions"

    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.telegram_id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    transaction_hash: Mapped[str] = mapped_column(default=str(uuid4()))
    transaction_type: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    confirmed_at: Mapped[datetime] = mapped_column(nullable=True, default=None)


class LotteryTransactions(Model):
    __tablename__ = "lottery_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.telegram_id"))
    amount: Mapped[float] = mapped_column(nullable=False)
    multiplier: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    confirmed_at: Mapped[datetime] = mapped_column(nullable=True)
