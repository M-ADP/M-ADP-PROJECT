import os
from typing import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

class BaseEntity(DeclarativeBase):
    pass


def _build_db_url() -> str:
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "madp")
    return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db_name}"


engine = create_async_engine(_build_db_url(), echo=False, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


async def create_all_tables() -> None:
    # 모델을 명시적으로 불러와 메타데이터에 등록
    from app.project import models as project_models  # noqa: F401
    from app.port import models as port_models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
