from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session
