from functools import lru_cache
from typing import AsyncIterator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.common.config.settings import get_db_config


class BaseEntity(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    db_config = get_db_config()
    return create_async_engine(db_config.url, echo=False, pool_pre_ping=True)


@lru_cache
def get_session_factory():
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session


_MIGRATIONS: list[tuple[str, list[str]]] = [
    (
        "001_init_role",
        [
            """
            UPDATE project_member
            SET role = 'MEMBER'
            WHERE role NOT IN ('OWNER', 'MEMBER')
            """,
        ],
    ),
    (
        "002_user_id_to_bigint",
        [
            "DELETE FROM project WHERE user_id REGEXP '[^0-9]'",
            "ALTER TABLE project MODIFY COLUMN user_id BIGINT NOT NULL",
        ],
    ),
    (
        "003_member_user_id_to_bigint",
        [
            "DELETE FROM project_member WHERE user_id REGEXP '[^0-9]'",
            "ALTER TABLE project_member MODIFY COLUMN user_id BIGINT NOT NULL",
        ],
    ),
]


async def create_all_tables() -> None:
    db_config = get_db_config()

    try:
        async with get_engine().begin() as conn:
            await conn.run_sync(BaseEntity.metadata.create_all)
            await conn.execute(text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(64) PRIMARY KEY,
                    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            ))
            for version, sqls in _MIGRATIONS:
                result = await conn.execute(
                    text("SELECT 1 FROM schema_migrations WHERE version = :v"),
                    {"v": version},
                )
                if result.fetchone() is None:
                    for sql in sqls:
                        await conn.execute(text(sql))
                    await conn.execute(
                        text("INSERT INTO schema_migrations (version) VALUES (:v)"),
                        {"v": version},
                    )
    except OperationalError as exc:
        raise RuntimeError(
            "MySQL 연결에 실패했습니다. "
            f"대상: {db_config.host}:{db_config.port}/{db_config.name}. "
            "환경변수 DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME 설정과 DB 서버 기동 상태를 확인하세요."
        ) from exc
