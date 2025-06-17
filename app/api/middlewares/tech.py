from typing import Awaitable, Callable

from fastapi import HTTPException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.db.actions import TechActions


class TechWorksMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if TechActions().is_tech_works():
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, detail="Технические работы"
            )

        return await call_next(request)
