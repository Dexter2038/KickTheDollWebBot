import asyncio

import schedule
import uvicorn

from app import telegram_bot
from app.api import app
from app.db.actions import clear_game_sessions, mark_guess_games


def task_mark_guess_games():
    asyncio.run_coroutine_threadsafe(
        coro=mark_guess_games(), loop=asyncio.get_running_loop()
    )


def task_clear_game_sessions():
    asyncio.run_coroutine_threadsafe(
        coro=clear_game_sessions(), loop=asyncio.get_running_loop()
    )


async def start_uvicorn() -> None:
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config=config)
    await server.serve()


async def start_bot() -> None:
    bot, dp = await telegram_bot.get_bot()
    await dp.start_polling(bot)


async def main() -> None:
    await asyncio.gather(start_bot(), start_uvicorn())


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(clear_game_sessions)
    schedule.every().hour.at(":00").do(task_mark_guess_games)
    asyncio.run(main())
