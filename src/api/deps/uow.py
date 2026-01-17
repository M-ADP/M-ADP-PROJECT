from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.db import get_db_session
from src.infra.db.uow import SQLAlchemyUnitOfWork


async def get_uow(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncIterator[SQLAlchemyUnitOfWork]:
    uow = SQLAlchemyUnitOfWork(session)
    try:
        yield uow
    finally:
        await uow.session.close()
