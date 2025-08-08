from sqlalchemy.ext.asyncio import AsyncSession


async def create_refresh_token(session: AsyncSession, user_id: int) -> str:
    pass


async def create_access_token(user_id: int) -> str:
    pass
