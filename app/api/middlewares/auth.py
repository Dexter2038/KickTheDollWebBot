from typing import Awaitable, Callable, Optional, cast
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette import status

# from app.api.jwt import UserAuthManager


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        auth = request.cookies.get("Authorization")
        leave = RedirectResponse("/reg")

        if not auth:
            return leave

        payload = UserAuthManager().decode_token(auth[7:])

        sub = cast(Optional[str], payload.get("sub") if payload else None)

        if not (sub and sub.isdigit()):
            return leave

        request.state.user_id = int(sub)

        return await call_next(request)
