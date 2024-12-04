from datetime import datetime
from typing import List, Tuple

from pytz import UTC
from app.database import db

end_time = datetime.now(UTC)

def is_current_lottery() -> bool:
    return end_time > datetime.now(UTC)

async def get_top_winners() -> List[Tuple[str, float, int]]:
    return (await db.get_top_lottery_transactions())


async def make_deposit(user_id, multiplier, amount):
    await db.insert_lottery_transaction(user_id, multiplier, amount)
    return True

async def get_current_lottery() -> Tuple[datetime, float]:
    if is_current_lottery():
        return end_time, (await db.get_lottery_transactions_sum())
    return 0, 0


def create_lottery(date: str) -> bool:
    global end_time
    try:
        end_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
    except:
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
    except:
        end_time = save_time
        return False
    return True