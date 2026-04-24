from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import ProjectNotFound
from src.app.project.schemas import ProjectUniqueUsersResponse
from src.core.client.project_monitoring import ProjectMonitoringClient
from src.core.uow import UnitOfWork
from src.dependencies.client.monitoring import get_monitoring_client
from src.dependencies.uow import get_uow


class GetProjectUniqueUsersUseCase(BaseUseCase):
    """프로젝트의 고유 사용자 (DAU/WAU/MAU) 조회"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        monitoring_client: ProjectMonitoringClient = Depends(get_monitoring_client),
    ):
        self.uow = uow
        self.monitoring_client = monitoring_client

    async def __call__(self, project_id: int, user_id: int) -> ProjectUniqueUsersResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

        data = await self.monitoring_client.get_unique_users(str(project_id))
        return ProjectUniqueUsersResponse(
            project_id=project_id,
            dau=data.dau,
            wau=data.wau,
            mau=data.mau,
        )
