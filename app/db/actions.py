from datetime import UTC, datetime, timedelta
from typing import List, Optional, Tuple, cast
from uuid import uuid4

import aiohttp
from bs4 import BeautifulSoup
from fastapi import HTTPException
from app.services.telegram import get_telegram_vars
from loguru import logger
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from .models import (
    Bets,
    FinishedGame,
    LotteryTransactions,
    Referrals,
    Transactions,
    Users,
)

end_time = datetime.now(UTC)

works_time = datetime.now(UTC)


class TechActions:
    def start_works(self, date: str) -> bool:
        global works_time
        try:
            works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
        except ValueError:
            works_time = datetime.now(UTC)
            return False
        return True

    def is_tech_works(self) -> bool:
        return works_time > datetime.now(UTC)

    def create_tech_works(self, date: str) -> bool:
        global works_time
        try:
            works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
        except ValueError:
            return False
        return True

    def change_date_tech_works(self, date: str) -> bool:
        global works_time
        save_time = works_time
        try:
            works_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
        except ValueError:
            works_time = save_time
            return False
        return True

    def end_tech_works(self) -> bool:
        global works_time
        works_time = datetime.now(UTC)
        return True


class LotteryActions:
    def is_current_lottery(self) -> bool:
        return end_time > datetime.now(UTC)

    def create_lottery(self, date: str) -> bool:
        global end_time
        try:
            end_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
        except ValueError:
            return False
        return True

    def close_lottery(self) -> bool:
        global end_time
        end_time = datetime.now(UTC)
        return True

    def change_date_lottery(self, date: str) -> bool:
        global end_time
        save_time = end_time
        try:
            end_time = datetime.strptime(date, "%d:%m:%Y.%H:%M:%S").astimezone(UTC)
        except ValueError:
            end_time = save_time
            return False
        return True


class Actions:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def login_user(self, init_data: str, wallet_address: str) -> Optional[int]:
        """
        Login user

        Args:
            init_data (str): Init data

        Returns:
            bool: True if user was logged in successfully, False otherwise
        """
        if not (vars := get_telegram_vars(init_data)):
            return None

        user = vars.get("telegram_id")
        if not user:
            return None

        telegram_id = user.get("id")
        if not telegram_id:
            return None

        username = user.get("username")
        if not username:
            return None

        if not await self.create_user(telegram_id, username, wallet_address):
            return None

        return telegram_id

    async def get_top_winners(self) -> List[Tuple[str, float, int]]:
        return await self.get_top_lottery_transactions()

    async def make_deposit(self, user_id: int, multiplier: float, amount: float):
        await self.insert_lottery_transaction(user_id, multiplier, amount)

    async def get_current_lottery(self) -> Tuple[datetime, float]:
        global end_time
        if LotteryActions().is_current_lottery():
            return end_time, await self.get_lottery_transactions_sum()
        return datetime.now(UTC), 0

    async def insert_lottery_transaction(
        self, user_id: int, multiplier: float, amount: float
    ) -> None:
        """
        Insert lottery transaction

        Args:
            user_id (int): User id
            multiplier (float): Multiplier
            amount (float): Amount
        """
        new_id = str(uuid4())
        if multiplier > 1:
            got = (amount * multiplier) - amount
            await self.add_user_money(user_id, got)
            await self.session.execute(
                insert(LotteryTransactions).values(
                    transaction_id=new_id,
                    telegram_id=user_id,
                    multiplier=multiplier,
                    amount=amount,
                    created_at=datetime.now(UTC),
                )
            )
        else:
            await self.minus_user_money(user_id, amount)

    async def get_username(self, user_id: int) -> str:
        """
        Get username by user_id

        Args:
            user_id (int): User id

        Returns:
            str: Username
        """
        query = select(Users.username).where(Users.telegram_id == user_id)
        result = await self.session.execute(query)
        username = result.scalar()
        return username or ""

    async def invest_game_money(self, user_id: int, amount: float) -> bool:
        """
        Minus money from user's balance and add to game's balance

        Args:
            user_id (int): User id
            amount (float): Amount of money

        Returns:
            bool: True if money was added successfully, False otherwise
        """
        statement = (
            update(Users)
            .where(Users.telegram_id == user_id)
            .values(money_balance=Users.money_balance + amount)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            # TODO
            # statement = update(Games).where(
            #     Games.id == 1).values(
            #         balance=Games.balance + amount)
            # await session.execute(statement)
            return True  # User found and updated successfully
        else:
            return False  # User not found

    async def get_lottery_transactions_sum(self) -> float:
        """
        Get sum of all lottery transactions

        Returns:
            float: Sum of all lottery transactions
        """
        query = select(
            func.sum(
                (LotteryTransactions.amount * LotteryTransactions.multiplier)
                - LotteryTransactions.amount
            )
        ).select_from(LotteryTransactions)
        result = await self.session.execute(query)
        total = result.scalar()
        return total or 0

    async def get_top_lottery_transactions(self) -> List[Tuple[str, float, int]]:
        """
        Get top lottery transactions

        Returns:
            List[Tuple[str, float, int]]: List of tuples with username, multiplier and bet
        """
        query = (
            select(
                LotteryTransactions.telegram_id,
                LotteryTransactions.multiplier,
                LotteryTransactions.amount,
            )
            .order_by(LotteryTransactions.amount.desc())
            .limit(10)
        )
        result = await self.session.execute(query)
        rows = result.all()
        top_transactions = [
            (await self.get_username(user_id), multiplier, amount)
            for user_id, multiplier, amount in rows
        ]

        return top_transactions

    async def add_user_wallet(self, telegram_id: int, wallet_address: str) -> bool:
        """
        Adds wallet to user

        Args:
            telegram_id (str): Telegram ID of the user
            wallet_address (str): The wallet address to add

        Returns:
            bool: True if wallet was added successfully, False otherwise
        """
        statement = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(wallet_address=wallet_address)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            return True  # User found and updated successfully
        else:
            return False  # User not found

    async def remove_user_wallet(self, telegram_id: int) -> bool:
        """
        Removes wallet from user

        Args:
            telegram_id (str): Telegram ID of the user

        Returns:
            bool: True if wallet was removed successfully, False otherwise
        """
        statement = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(wallet_address=None)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            return True
        else:
            return False

    async def get_referral_count(self, user_id: int) -> int:
        """
        Get count of referrals of certain user

        Args:
            user_id (int): User id

        Returns:
            int: Count of referrals
        """
        query = (
            select(func.count())
            .select_from(Referrals)
            .where(Referrals.referrer_id == user_id)
        )
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0

    async def take_referral_reward(self, user_id: int) -> float:
        """
        Take all referral rewards

        Args:
            user_id (int): User id

        Returns:
            float: Amount of reward
        """
        query = (
            select(func.sum(Referrals.bonus))
            .select_from(Referrals)
            .where(Referrals.referrer_id == user_id)
        )
        result = await self.session.execute(query)
        count = result.scalar() or 0
        query = (
            update(Referrals).where(Referrals.referrer_id == user_id).values(bonus=0)
        )
        # TODO: money to user
        await self.session.execute(query)
        return count

    async def get_referral_reward(self, user_id: int) -> float:
        """
        Get amount of reward for every of referal

        Args:
            user_id (int): User id

        Returns:
            float: Amount of reward
        """
        query = (
            select(func.sum(Referrals.bonus))
            .select_from(Referrals)
            .where(Referrals.referrer_id == user_id)
        )
        result = await self.session.execute(query)
        reward = result.scalar()
        return reward or 0

    async def create_user(
        self, telegram_id: int, username: str, wallet_address: str
    ) -> bool:
        """
        Creates a new user in the database.

        Args:
            telegram_id (int): The Telegram ID of the user.
            username (str): The username of the user.
            wallet_address (str): The wallet address of the user.

        Returns:
            int: The ID of the newly created user or already existing one.
        """
        logger.info(
            f"Создан новый пользователь: Telegram ID: {telegram_id}, Никнейм: {username}, Адресс кошелька: {wallet_address}"
        )

        res = await self.session.execute(
            select(Users.telegram_id).where(Users.telegram_id == telegram_id)
        )
        user_id = res.scalar_one_or_none()

        if user_id is not None:
            return True

        model = Users(
            telegram_id = telegram_id,
            username = username,
            wallet_address = wallet_address
        )
        self.session.add(model)
        try:
            await self.session.commit()
        except:
            return False
        return True

    async def get_user(self, telegram_id: int) -> Users:
        """
        Retrieves a user from the database based on their Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user to retrieve.

        Returns:
            Users: The user object if found, otherwise None.

        Example:
            >>> await get_user("1234567890")
            Users(id=1, telegram_id="1234567890", username="JohnDoe")
        """
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(query)
        curr = result.scalars()
        user = curr.first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def clear_user(self, telegram_id: int) -> bool:
        """
        Deletes a user from the database based on their Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user to delete.

        Returns:
            bool: True if the user was found and deleted successfully, False otherwise.

        Example:
            >>> await clear_user("1234567890")
            True
        """
        logger.info(f"Пользователь {telegram_id} был удален")
        statement = delete(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(statement)
        return result.rowcount > 0

    async def add_user_money(self, telegram_id: int, money: float) -> bool:
        """
        Adds a specified amount of money to a user's balance.

        Args:
            telegram_id (int): The Telegram ID of the user.
            money (float): The amount of money to add to the user's balance.

        Returns:
            bool: True if the user was found and their balance was updated successfully, False otherwise.

        Example:
            >>> await add_user_money("123456789", 100)  # Add 100 units of money to user with Telegram ID "123456789"
            True
        """
        logger.info(
            f"На баланс пользователя {telegram_id} было добавлено {money} монет"
        )
        statement = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(money_balance=Users.money_balance + money)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            return True  # User found and updated successfully
        else:
            return False  # User not found

    async def subtract_user_money(self, telegram_id: int, money: int) -> bool:
        """
        Subtract a specified amount of money from a user's balance.

        Args:
            telegram_id (str): The Telegram ID of the user.
            money (int): The amount of money to subtract.

        Returns:
            bool: True if the user was found and the balance was updated successfully, False otherwise.

        Example:
            >>> await subtract_user_money("123456789", 100)
            True  # User with Telegram ID "123456789" had 100 units of money subtracted from their balance.

        Notes:
            This function uses a database transaction to ensure atomicity.
        """
        logger.info(f"С баланса пользователя {telegram_id} было вычтено {money} монет")
        statement = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(money_balance=Users.money_balance - money)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            return True  # User found and updated successfully
        else:
            return False  # User not found

    async def delete_user(self, telegram_id: int) -> bool:
        """Functions that deletes user based on their telegram ID

        Args:
            telegram_id (str): Telegram ID of the user who will be deleted

        Returns:
            bool: True if the user was deleted, False otherwise
        """
        logger.info(f"Удалён пользователь: {telegram_id}")
        statement = delete(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(statement)
        return result.rowcount > 0  # True if deletion was successful, False otherwise.

    async def create_transaction(
        self, user_id: str, amount: float, transaction_type: int
    ) -> bool:
        """
        Creates a new transaction.

        Args:
            telegram_id (str): The Telegram ID of the user.
            amount (float): The amount of the transaction.
            transaction_type (int): The type of the transaction (e.g. 1 for deposit, 2 for withdrawal).

        Returns:
            bool: True if the transaction is created successfully, False otherwise.

        Example:
            >>> await create_transaction("123456789", 100, 1)
        """
        logger.info(
            f"Создана транзакция: Пользователь: {user_id}, Сумма: {amount}, Тип: {'Вывод' if transaction_type else 'Депозит'}"
        )
        try:
            model = Transactions(
                user_id=user_id, amount=amount, transaction_type=transaction_type
            )
            self.session.add(model)
            await self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating transaction: {e.__class__.__name__}: {e}")
            return False

    async def create_bet(
        self, user_id: int, coin: str, amount: float, shift_hours: int, way: int
    ) -> bool:
        logger.info(
            f"Сделана ставка: Пользователь: {user_id}, Сумма: {amount}, На время: {shift_hours} д вперёд"
        )
        try:
            created_at = datetime.now(UTC)
            supposed_at = created_at + timedelta(hours=shift_hours)
            start_value = ...  # TODO
            model = Bets(
                user_id=user_id,
                amount=amount,
                coin=coin,
                supposed_at=supposed_at,
                start_value=start_value,
            )
            self.session.add(model)
            await self.session.commit()
            return True
        except Exception as e:
            print(f"Error creating bet: {e.__class__.__name__}: {e}")
            return False

    async def get_bets(self, user_id: int) -> List[Bets]:
        query = select(Bets).where(Bets.user_id == user_id)
        result = await self.session.execute(query)
        bets = result.scalars().fetchall()
        return cast(List[Bets], bets)

    async def minus_user_money(self, telegram_id: int, money: float) -> bool:
        """
        Minus a specified amount of money from a user's balance.

        Args:
            telegram_id (int): The Telegram ID of the user.
            money (int): The amount of money to minus from the user's balance.

        Returns:
            bool: True if the user was found and their balance was updated successfully, False otherwise.

        Example:
            >>> await minus_user_money("123456789", 100)  # Minus 100 units of money from user with Telegram ID "123456789"
        True
        """
        logger.info(f"С баланса пользователя {telegram_id} было вычтено {money} монет")
        statement = (
            update(Users)
            .where(Users.telegram_id == telegram_id)
            .values(money_balance=Users.money_balance - money)
        )
        result = await self.session.execute(statement)
        if result.rowcount > 0:
            return True  # User found and updated successfully
        else:
            return False  # User not found

    async def mark_finished_game(
        self,
        game_type: int,
        amount: int | float,
        first_user_id: int,
        second_user_id: int | None = None,
        game_hash: str | None = None,
    ) -> bool:
        """
        Create finished game model and add it to database
        """
        logger.info(
            f"Игра помечена завершённой: Тип игры: {game_type}, Сумма: {amount}, ID 1-го игрока: {first_user_id}, ID 2-го игрока: {second_user_id}"
        )
        try:
            model = FinishedGame(
                game_type=game_type,
                amount=amount,
                first_user_id=first_user_id,
                second_user_id=second_user_id,
                game_hash=game_hash,
            )
            self.session.add(model)
            if game_type > 2:
                if amount > 0:
                    await self.add_user_money(first_user_id, amount)
                elif amount < 0:
                    await self.minus_user_money(first_user_id, -amount)
            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating finished game: {e.__class__.__name__}: {e}")
            return False

    async def get_finished_games(self) -> List[FinishedGame]:
        """
        Get all finished games
        """
        query = select(FinishedGame)
        result = await self.session.execute(query)
        games = result.scalars().all()
        return cast(List[FinishedGame], games)

    async def get_count_users(self) -> int:
        """
        Get count of all users
        """
        query = select(func.count()).select_from(Users)
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0

    async def get_users(self, page: int = 1) -> List[Users]:
        """
        Get list of users

        Args:
            page (int): Page number

        Returns:
            List[Users]: List of users
        """
        query = select(Users).offset((page - 1) * 10).limit(10)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return cast(List[Users], users)

    async def edit_money_balance(self, telegram_id: int, money_balance: float) -> bool:
        logger.info(
            f"Был изменён монетный баланс пользователя {telegram_id} на {money_balance}"
        )
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar()
        if user is None:
            return False
        user.money_balance = money_balance
        await self.session.commit()
        return True

    async def add_user_money_balance(
        self, telegram_id: int, money_balance: float | int
    ) -> bool:
        logger.info(
            f"На баланс пользователя {telegram_id} было добавлено {money_balance} монет"
        )
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar()
        if user is None:
            return False
        user.money_balance += money_balance
        await self.update_referrers_balance(telegram_id, money_balance * 0.025)
        await self.session.commit()
        return True

    async def update_referrers_balance(
        self, referred_telegram_id: int, bonus_amount: float
    ) -> None:
        """
        Recursively updates the balance for all referrers of a referred user.

        Args:
            referred_telegram_id (int): Telegram ID of the referred user.
            bonus_amount (float): The amount to add to referrers' balances.
        """
        if bonus_amount < 5:
            return
        # Find the referral relationship where the referred user matches
        query = select(Referrals).where(
            Referrals.referrer_id == referred_telegram_id, Referrals.status.is_(True)
        )
        result = await self.session.execute(query)
        referral = result.scalar()

        # If no referral relationship exists, exit the recursion
        if not referral:
            return

        # Find the referrer (the user who referred the current user)
        referral.bonus += bonus_amount
        query = select(Referrals).where(Referrals.referred_id == referral.referrer_id)
        result = await self.session.execute(query)
        referrer = result.scalar()
        if referrer:
            # Recursively update the balance of the next referrer up the chain
            await self.update_referrers_balance(
                referrer.referred_id, bonus_amount * 0.025
            )

    async def edit_dollar_balance(
        self, telegram_id: int, dollar_balance: float
    ) -> bool:
        logger.info(
            f"Был изменён долларовый баланс пользователя {telegram_id} на {dollar_balance}"
        )
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar()
        if user is None:
            return False
        user.money_balance = dollar_balance
        await self.session.commit()
        return True

    async def get_count_transactions(self) -> int:
        """
        Get count of all transactions
        """
        query = select(func.count()).select_from(Transactions)
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0

    async def get_transactions(self, page: int = 1) -> List[Transactions]:
        """
        Get list of transactions

        Args:
            page (int): Page number

        Returns:
            List[Transactions]: List of transactions
        """
        query = select(Transactions).offset((page - 0) * 10).limit(10)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return cast(List[Transactions], transactions)

    async def get_game_params(
        self, telegram_id: int
    ) -> Tuple[float, bool, bool, datetime]:
        """
        Get game params (money balance and available bonus)

        Args:
            telegram_id (str | int): Telegram id

        Returns:
            tuple: Money balance and available bonus
        """
        query = select(
            Users.money_balance,
            Users.bonuses_to_bot > 0,
            (Users.last_visit_to_bot < datetime.now(UTC) - timedelta(hours=4)),
            Users.last_visit_to_bot,
        ).where(Users.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_transactions(self, user_id: int) -> List[Transactions]:
        """
        Get list of user transactions

        Args:
            user_id (int): User id

        Returns:
            List[Transactions]: List of transactions
        """
        query = select(Transactions).where(Transactions.telegram_id == user_id)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return cast(List[Transactions], transactions)

    async def get_transaction(self, transaction_id: int):
        query = select(Transactions).where(
            Transactions.transaction_id == transaction_id
        )
        result = await self.session.execute(query)
        transaction = result.scalars().first()
        return transaction

    async def confirm_transaction(self, transaction_id: int) -> bool:
        logger.info(f"Подтверждена транзакция: {transaction_id}")
        query = select(Transactions).where(
            Transactions.transaction_id == transaction_id
        )
        result = await self.session.execute(query)
        transaction = result.scalars().first()
        if not transaction:
            return False
        transaction.confirmed_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def get_count_referrals(self) -> int:
        """
        Get count of all referalls
        """
        query = select(func.count()).select_from(Referrals)
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0

    async def get_referral(self, id: int) -> Optional[Referrals]:
        """
        Get referral

        Args:
            id (int): User id

        Returns:
            Referrals: Referral
        """
        query = select(Referrals).where(Referrals.referrer_id == id)
        result = await self.session.execute(query)
        referral = result.scalars().first()
        return referral

    async def get_referrals(self, page: int = 1) -> List[Referrals]:
        """
        Get list of referrals

        Args:
            page (int): Page number

        Returns:
            List[Referrals]: List of referrals
        """
        # TODO: REMADE
        query = select(Referrals).offset((page - 1) * 10).limit(10)
        result = await self.session.execute(query)
        referrals = result.scalars().all()
        return cast(List[Referrals], referrals)

    async def get_sum_lottery_transactions(self) -> float:
        query = select(func.sum(LotteryTransactions.amount)).select_from(
            LotteryTransactions
        )
        result = await self.session.execute(query)
        sum = result.scalar()
        return sum or 0

    async def get_count_lottery_transactions(self) -> int:
        query = select(func.count()).select_from(LotteryTransactions)
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0

    async def get_lottery_transactions(
        self, page: int = 1
    ) -> List[LotteryTransactions]:
        """
        Get list of lottery transactions

        Args:
            page (int): Page number

        Returns:
            List[LotteryTransactions]: List of lottery transactions
        """
        query = select(LotteryTransactions).offset((page - 1) * 10).limit(10)
        result = await self.session.execute(query)
        transactions = result.scalars().all()
        return cast(List[LotteryTransactions], transactions)

    async def check_admin(self, telegram_id: int) -> bool:
        query = (
            select(Users)
            .where(Users.telegram_id == telegram_id)
            .where(Users.admin.is_(True))
        )
        result = await self.session.execute(query)
        user = result.scalars().first()
        return bool(user)

    async def delete_referral(self, referral_id: int) -> bool:
        logger.info(f"Удалена рефералка: {referral_id}")
        query = select(Referrals).where(Referrals.referral_id == referral_id)
        result = await self.session.execute(query)
        referral = result.scalars().first()
        await self.session.delete(referral)
        await self.session.commit()
        return True

class JWTActions(Actions):
    async def 


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


async def mark_guess_games():
    async with aiohttp.ClientSession(
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
    ) as session:
        html = await fetch(session, "https://coinmarketcap.com")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody")
        trs = table.find_all("tr", limit=20)
        coins = dict()
        for tr in trs:
            tds = tr.find_all("td")
            price = tds[3].get_text()
            value, _ = tds[2].get_text(" ", strip=True).rsplit(" ", maxsplit=1)
            coins[value] = price
    async for session in get_session():
        query = select(Bets).where(Bets.supposed_at <= datetime.now(UTC))
        result = await session.execute(query)
        bets = result.scalars().all()
        actions = Actions(session)
        for bet in bets:
            if coins[bet.coin] < bet.start_value:
                if bet.way == -1:
                    await actions.add_user_money(bet.user_id, bet.amount)
                else:
                    await actions.minus_user_money(bet.user_id, bet.amount)
            else:
                if bet.way == -1:
                    await actions.minus_user_money(bet.user_id, bet.amount)
                else:
                    await actions.add_user_money(bet.user_id, bet.amount)


async def clear_game_sessions():
    """
    Clear all game sessions
    """
    async for session in get_session():
        statement = update(Users).values(
            last_visit_to_bot=datetime.now(UTC) - timedelta(hours=5),
            bonuses_to_bot=3,
        )
        await session.execute(statement)
