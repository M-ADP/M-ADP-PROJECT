from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import OnlyOwnerCanGetResourceLimit, ProjectNotFound
from src.app.project.schemas import ProjectResourceLimitResponse
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class GetProjectResourceLimitUseCase(BaseUseCase):
    """프로젝트 최대 리소스 한도를 조회합니다."""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
    ):
        self.uow = uow

    async def __call__(self, project_id: int, user_id: int) -> ProjectResourceLimitResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanGetResourceLimit()

            return ProjectResourceLimitResponse(
                project_id=project.id,
                max_cpu=project.max_cpu,
                max_memory=project.max_memory,
                max_disk=project.max_disk,
            )
