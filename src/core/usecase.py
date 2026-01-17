from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends

from src.api.deps.project_resource_client import get_project_resource_client
from src.api.deps.uow import get_uow
from src.common.client.project_resource import ProjectResourceClient
from src.core.uow import UnitOfWork


class BaseUseCase(ABC):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(
            get_project_resource_client
        ),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await self.execute(*args, **kwargs)

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """실제 비즈니스 로직을 구현하는 추상 메서드"""
        pass
