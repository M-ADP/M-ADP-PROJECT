from abc import ABC, abstractmethod
from typing import Self

from src.core.repository import (
    ProjectRepository,
    ProjectMemberRepository,
)


class UnitOfWork(ABC):
    """추상 Unit of Work 클래스"""
    project: ProjectRepository
    project_member: ProjectMemberRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass
