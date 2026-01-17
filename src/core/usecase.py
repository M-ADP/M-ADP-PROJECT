from abc import ABC, abstractmethod
from typing import Any

from src.core.uow import UnitOfWork


class BaseUseCase(ABC):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await self.execute(*args, **kwargs)

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """실제 비즈니스 로직을 구현하는 추상 메서드"""
        pass
