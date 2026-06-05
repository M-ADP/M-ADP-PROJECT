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
    return create_async_engine(db_config.url, echo=False, pool_recycle=1800)


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
    (
        "004_project_invitation",
        [
            """
            CREATE TABLE IF NOT EXISTS project_invitation (
                id BIGINT NOT NULL PRIMARY KEY,
                project_id BIGINT NOT NULL,
                inviter_user_id BIGINT NOT NULL,
                invitee_user_id BIGINT NOT NULL,
                invitee_email VARCHAR(255) NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                responded_at DATETIME NULL,
                CONSTRAINT fk_project_invitation_project
                    FOREIGN KEY (project_id) REFERENCES project(id)
                    ON DELETE CASCADE
            )
            """,
            """
            SET @column_exists = (
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND COLUMN_NAME = 'token_hash'
            )
            """,
            """
            SET @sql = IF(
                @column_exists = 0,
                'ALTER TABLE project_invitation ADD COLUMN token_hash VARCHAR(255) NULL',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
            """
            SET @column_exists = (
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND COLUMN_NAME = 'expires_at'
            )
            """,
            """
            SET @sql = IF(
                @column_exists = 0,
                'ALTER TABLE project_invitation ADD COLUMN expires_at DATETIME NULL',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
            """
            UPDATE project_invitation
            SET token_hash = SHA2(CONCAT('expired:', id, ':', UUID()), 256),
                status = 'EXPIRED',
                responded_at = COALESCE(responded_at, CURRENT_TIMESTAMP)
            WHERE token_hash IS NULL OR token_hash = ''
            """,
            """
            UPDATE project_invitation
            SET expires_at = COALESCE(expires_at, created_at, CURRENT_TIMESTAMP)
            WHERE expires_at IS NULL
            """,
            "ALTER TABLE project_invitation MODIFY COLUMN token_hash VARCHAR(255) NOT NULL",
            "ALTER TABLE project_invitation MODIFY COLUMN expires_at DATETIME NOT NULL",
            """
            SET @index_exists = (
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND INDEX_NAME = 'ix_project_invitation_project_id'
            )
            """,
            """
            SET @sql = IF(
                @index_exists = 0,
                'CREATE INDEX ix_project_invitation_project_id ON project_invitation (project_id)',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
            """
            SET @index_exists = (
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND INDEX_NAME = 'ix_project_invitation_invitee_user_id'
            )
            """,
            """
            SET @sql = IF(
                @index_exists = 0,
                'CREATE INDEX ix_project_invitation_invitee_user_id ON project_invitation (invitee_user_id)',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
            """
            SET @index_exists = (
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND INDEX_NAME = 'uq_project_invitation_token_hash'
            )
            """,
            """
            SET @sql = IF(
                @index_exists = 0,
                'CREATE UNIQUE INDEX uq_project_invitation_token_hash ON project_invitation (token_hash)',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
            """
            SET @index_exists = (
                SELECT COUNT(*)
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'project_invitation'
                  AND INDEX_NAME = 'uq_project_invitation_status'
            )
            """,
            """
            SET @sql = IF(
                @index_exists = 0,
                'CREATE UNIQUE INDEX uq_project_invitation_status ON project_invitation (project_id, invitee_user_id, status)',
                'SELECT 1'
            )
            """,
            "PREPARE stmt FROM @sql",
            "EXECUTE stmt",
            "DEALLOCATE PREPARE stmt",
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
