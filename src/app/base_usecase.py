from fastapi import Depends

from src.api.deps.uow import get_uow
from src.api.deps.project_resource_client import get_project_resource_client
from src.common.client.project_resource import ProjectResourceClient
from src.core.uow import UnitOfWork


class BaseUseCase:
    def __init__(
            self,
            uow : UnitOfWork = Depends(get_uow),
            project_resource_client: ProjectResourceClient = Depends(
                get_project_resource_client
            ),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client
