from datetime import UTC, datetime
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.actions import Actions

end_time = datetime.now(UTC)


def is_current_lottery() -> bool:
    return end_time > datetime.now(UTC)


async def get_top_winners(session: AsyncSession) -> List[Tuple[str, float, int]]:
    return await Actions(session).get_top_lottery_transactions()


async def make_deposit(
    session: AsyncSession, user_id: int, multiplier: float, amount: float
):
    await Actions(session).insert_lottery_transaction(user_id, multiplier, amount)


async def get_current_lottery(session: AsyncSession) -> Tuple[datetime, float]:
    global end_time
    if is_current_lottery():
        return end_time, (await Actions(session).get_lottery_transactions_sum())
    return datetime.now(UTC), 0


def create_lottery(date: str) -> bool:
    global end_time
    try:
        end_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except ValueError:
        return False
    return True


def close_lottery() -> bool:
    global end_time
    end_time = datetime.now(UTC)
    return True


def change_date_lottery(date: str) -> bool:
    global end_time
    save_time = end_time
    try:
        end_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except ValueError:
        end_time = save_time
        return False
    return True
