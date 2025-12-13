from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.db import get_db_session
from app.project import repository


@dataclass
class UserInfo:
    user_id: str
    role: str


async def get_user_info(
    user_id: str = Header(..., alias="user-id", description="사용자 식별자"),
    role: str = Header(..., alias="role", description="사용자 역할"),
) -> UserInfo:
    return UserInfo(user_id=user_id, role=role)
