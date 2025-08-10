from typing import Awaitable, Callable

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from backend.db.actions import TechActions


class TechWorksMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not TechActions().is_tech_works():
            return await call_next(request)

        return JSONResponse(
            {"detail": "Технические работы"}, status.HTTP_503_SERVICE_UNAVAILABLE
        )
