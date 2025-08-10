from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram3_di import setup_di
from loguru import logger

from backend.config import settings

from .handlers import get_routers


async def get_bot_username(bot: Bot) -> str:
    info = await bot.get_me()
    return info.username or ""


async def get_bot() -> Tuple[Bot, Dispatcher]:
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(get_routers())
    setup_di(dp)
    logger.info(f"Бот {await get_bot_username(bot)} готов!")
    return bot, dp
