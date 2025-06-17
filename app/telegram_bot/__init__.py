from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram3_di import setup_di
from loguru import logger

from app.config import settings

from .handlers import get_routers


def get_bot() -> Tuple[Bot, Dispatcher]:
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(get_routers())
    setup_di(dp)
    logger.info("Бот готов!")
    return bot, dp
