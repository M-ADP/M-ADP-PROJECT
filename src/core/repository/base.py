from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """추상 Repository 기본 클래스"""

    def __init__(self, session: AsyncSession):
        self._session = session