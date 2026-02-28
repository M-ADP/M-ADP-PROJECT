from dataclasses import dataclass

from fastapi import Header


@dataclass
class UserInfo:
    user_id: int
    role: str


async def get_user_info(
    user_id: int = Header(..., alias="X-User-Id", description="사용자 식별자"),
    role: str = Header(..., alias="X-User-Role", description="사용자 역할"),
) -> UserInfo:
    return UserInfo(user_id=user_id, role=role)
