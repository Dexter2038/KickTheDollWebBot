from aiogram import Bot, Dispatcher

from typing import Tuple
from os import environ
from loguru import logger
from aiogram3_di import setup_di

from .handlers import get_routers

try:
    bot = Bot(environ["bot_token"])
    dp = Dispatcher()
    dp.include_router(get_routers())
    setup_di(dp)
except KeyError:
    raise Exception("Please set your bot token in .env file")


def get_bot() -> Tuple[Bot, Dispatcher]:
    logger.info("Бот готов!")
    return bot, dp
