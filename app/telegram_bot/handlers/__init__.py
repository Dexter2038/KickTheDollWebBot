from aiogram import Router
from .balances import router as balance_router
from .lottery import router as lottery_router
from .referrals import router as referrals_router
from .history import router as history_router
from .tech import router as tech_router
from .users import router as users_router
from .main import router as main_router


def get_routers() -> Router:
    """
    Returns a Router instance that includes all routers from the application.
    
    The returned Router instance is initialized with the current module name and 
    includes the main, users, balance, lottery, referrals, history, and tech routers.
    
    Returns:
        Router: A Router instance that includes all routers from the application.
    """
    router = Router(name=__name__)
    router.include_router(main_router)
    router.include_router(users_router)
    router.include_router(balance_router)
    router.include_router(referrals_router)
    router.include_router(history_router)
    router.include_router(tech_router)
    router.include_router(lottery_router)
    return router


__all__ = ["get_routers"]
