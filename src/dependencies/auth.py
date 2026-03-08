import logging
from dataclasses import dataclass

from fastapi import Header

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    user_id: int
    role: str


async def get_user_info(
    user_id: str = Header(..., alias="X-User-Id", description="사용자 식별자"),
    role: str = Header(..., alias="X-User-Role", description="사용자 역할"),
) -> UserInfo:
    logger.error(f"[AUTH] X-User-Id={user_id!r}")  # 임시
    return UserInfo(user_id=int(user_id), role=role)
