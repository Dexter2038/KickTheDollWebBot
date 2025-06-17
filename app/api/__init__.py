from fastapi import FastAPI, HTTPException
from starlette.staticfiles import StaticFiles

from app import config
from app.api.middlewares.auth import AuthMiddleware
from app.api.middlewares.tech import TechWorksMiddleware
from app.api.routes.blackjack import router as blackjack_router
from app.api.routes.dice import router as dice_router
from app.api.routes.game import router as game_router
from app.api.routes.guess import router as guess_router
from app.api.routes.lottery import router as lottery_router
from app.api.routes.misc import router as misc_router
from app.api.routes.player import router as player_router
from app.api.routes.transaction import router as transaction_router
from app.api.routes.wallet import router as wallet_router


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


app = FastAPI(title="SPA App", docs_url=None, redoc_url=None, on_startup=config.init())
api_app = FastAPI(title="API App", docs_url=None, redoc_url=None)

app.mount(
    "/assets", StaticFiles(directory="app/assets", check_dir=False), name="assets"
)
app.mount("/api", api_app)
app.mount("/", SPAStaticFiles(directory="app/templates", html=True), name="index")

app.add_middleware(AuthMiddleware)
app.add_middleware(TechWorksMiddleware)


api_app.include_router(blackjack_router)
api_app.include_router(dice_router)
api_app.include_router(game_router)
api_app.include_router(guess_router)
api_app.include_router(lottery_router)
api_app.include_router(misc_router)
api_app.include_router(player_router)
api_app.include_router(transaction_router)
api_app.include_router(wallet_router)
