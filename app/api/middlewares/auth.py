from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.api.jwt import refresh_token, verify_access_token
from app.db.session import get_session


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        access_token = request.cookies.get("access_token")
        _refresh_token = request.cookies.get("refresh_token")

        leave = RedirectResponse("/reg")

        if not access_token and not _refresh_token:
            return leave

        user_id = verify_access_token(access_token)

        if user_id:
            request.state.user_id = user_id
            return await call_next(request)

        if not _refresh_token:
            return leave

        token = ""
        async for session in get_session():
            token, user_id = await refresh_token(session, _refresh_token)

        if not token:
            return leave

        request.state.user_id = user_id

        response = await call_next(request)

        response.set_cookie(
            "access_token", token, httponly=True, secure=True, samesite="strict"
        )
        return response
