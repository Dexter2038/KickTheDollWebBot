from datetime import UTC, datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.db.actions import RefreshTokenActions
from app.config import settings


async def create_refresh_token(
    session: AsyncSession, user_id: int, delta: timedelta
) -> Optional[str]:
    now = datetime.now(UTC)
    valid_till = now + delta
    jti = await RefreshTokenActions(session).create_refresh_token(user_id, valid_till)
    if not jti:
        return

    if now > valid_till:
        return

    try:
        token = jwt.encode(
            {"jti": jti, "iat": now, "exp": valid_till, "sub": user_id},
            key=settings.jwt_secret,
            algorithm="HS256",
        )
    except jwt.PyJWTError:
        return

    return token


async def create_access_token(user_id: int, delta: timedelta) -> Optional[str]:
    now = datetime.now(UTC)
    valid_till = now + delta
    if now > valid_till:
        return

    try:
        token = jwt.encode(
            {"sub": user_id, "iat": now, "exp": valid_till},
            key=settings.jwt_secret,
            algorithm="HS256",
        )
    except jwt.PyJWTError:
        return

    return token


async def verify_refresh_token(session: AsyncSession, token: str) -> Optional[int]:
    payload = jwt.decode(token, key=settings.jwt_secret, algorithms=["HS256"])
    return await RefreshTokenActions(session).verify_refresh_token(payload)


async def verify_access_token(token: str) -> Optional[int]:
    payload = jwt.decode(token, key=settings.jwt_secret, algorithms=["HS256"])
    sub = payload.get("sub")
    if not sub:
        return

    if not sub.isdigit():
        return

    sub = int(sub)

    iat = payload.get("iat")
    if not iat:
        return

    iat = datetime.fromtimestamp(iat, tz=UTC)

    exp = payload.get("exp")
    if not exp:
        return
    exp = datetime.fromtimestamp(exp, tz=UTC)

    if exp < datetime.now(UTC):
        return

    return sub


async def refresh_token(
    session: AsyncSession, token: str
) -> tuple[Optional[str], Optional[int]]:
    if not (user_id := await verify_refresh_token(session, token)):
        return None, None

    return await create_access_token(user_id, delta=timedelta(days=1)), user_id
