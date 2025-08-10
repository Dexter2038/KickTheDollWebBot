from fastapi import FastAPI

from backend import config
from backend.api.middlewares.auth import AuthMiddleware
from backend.api.middlewares.tech import TechWorksMiddleware
from backend.api.routes.blackjack import router as blackjack_router
from backend.api.routes.dice import router as dice_router
from backend.api.routes.game import router as game_router
from backend.api.routes.guess import router as guess_router
from backend.api.routes.lottery import router as lottery_router
from backend.api.routes.misc import router as misc_router
from backend.api.routes.player import router as player_router
from backend.api.routes.transaction import router as transaction_router
from backend.api.routes.wallet import router as wallet_router

app = FastAPI(on_startup=config.init())

app.add_middleware(AuthMiddleware)
app.add_middleware(TechWorksMiddleware)


app.include_router(blackjack_router)
app.include_router(dice_router)
app.include_router(game_router)
app.include_router(guess_router)
app.include_router(lottery_router)
app.include_router(misc_router)
app.include_router(player_router)
app.include_router(transaction_router)
app.include_router(wallet_router)
