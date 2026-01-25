from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends

from src.api.deps.deployment_client import get_deployment_client
from src.api.deps.deployment_summary_client import get_deployment_summary_client
from src.api.deps.project_resource_client import get_project_resource_client
from src.api.deps.user_client import get_user_client
from src.common.client.deployment import DeploymentClient
from src.common.client.deployment_summary import DeploymentSummaryClient
from src.api.deps.uow import get_uow
from src.common.client.project_resource import ProjectResourceClient
from src.common.client.user import UserClient
from src.core.uow import UnitOfWork


class BaseUseCase(ABC):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(
            get_project_resource_client
        ),
        deployment_summary_client: DeploymentSummaryClient = Depends(
            get_deployment_summary_client
        ),
        deployment_client: DeploymentClient = Depends(get_deployment_client),
        user_client: UserClient = Depends(get_user_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client
        self.deployment_summary_client = deployment_summary_client
        self.deployment_client = deployment_client
        self.user_client = user_client

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        async with self.uow:
            return await self.execute(*args, **kwargs)

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """실제 비즈니스 로직을 구현하는 추상 메서드"""
        pass
