import os
from typing import AsyncIterator

from dotenv import load_dotenv
from sqlalchemy import text
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


_MIGRATIONS: list[tuple[str, str]] = [
    (
        "001_init_role",
        """
        UPDATE project_member
        SET role = 'MEMBER'
        WHERE role NOT IN ('OWNER', 'MEMBER')
        """,
    ),
    (
        "002_user_id_to_bigint",
        """
        ALTER TABLE project
        MODIFY COLUMN user_id BIGINT NOT NULL
        """,
    ),
    (
        "003_member_user_id_to_bigint",
        """
        ALTER TABLE project_member
        MODIFY COLUMN user_id BIGINT NOT NULL
        """,
    ),
]


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseEntity.metadata.create_all)
        await conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(64) PRIMARY KEY,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        ))
        for version, sql in _MIGRATIONS:
            result = await conn.execute(
                text("SELECT 1 FROM schema_migrations WHERE version = :v"),
                {"v": version},
            )
            if result.fetchone() is None:
                await conn.execute(text(sql))
                await conn.execute(
                    text("INSERT INTO schema_migrations (version) VALUES (:v)"),
                    {"v": version},
                )
