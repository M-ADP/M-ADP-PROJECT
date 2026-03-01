from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.common.config.settings import get_db_config

db_config = get_db_config()

class BaseEntity(DeclarativeBase):
    pass


engine = create_async_engine(db_config.url, echo=False, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
