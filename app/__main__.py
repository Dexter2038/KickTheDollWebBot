import asyncio

import schedule
import uvicorn
from starlette.templating import Jinja2Templates

from app import telegram_bot
from app.db.actions import mark_guess_games


templates: Jinja2Templates = Jinja2Templates(directory="app/templates")

wallets = []


def task_mark_guess_games():
    asyncio.run_coroutine_threadsafe(
        coro=mark_guess_games, loop=asyncio.get_running_loop()
    )


def clear_game_sessions():
    asyncio.run_coroutine_threadsafe(
        coro=clear_game_sessions, loop=asyncio.get_running_loop()
    )


bot, dp = telegram_bot.get_bot()


async def start_uvicorn() -> None:
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config=config)
    await server.serve()


async def start_bot() -> None:
    await dp.start_polling(bot)


async def main() -> None:
    await asyncio.gather(start_bot(), start_uvicorn())


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(clear_game_sessions)
    schedule.every().hour.at(":00").do(task_mark_guess_games)
    asyncio.run(main())
