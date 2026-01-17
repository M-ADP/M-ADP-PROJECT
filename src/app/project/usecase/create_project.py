from src.app.project.schemas import ProjectCreate
from src.app.project.exceptions import (
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
)
from src.app.project.model import Project
from src.core.usecase import BaseUseCase

PROJECT_LIMIT = 3


class CreateProjectUseCase(BaseUseCase):
    """프로젝트를 생성하는 유즈케이스"""

    async def execute(
        self,
        request: ProjectCreate,
        user_id: str,
    ) -> Project:
        project_count = await self.uow.project.count_by_user(user_id)
        if project_count >= PROJECT_LIMIT:
            raise ProjectLimitExceeded()

        if await self.uow.project.exists_by_name(user_id, request.name):
            raise ProjectNameAlreadyExists()

        project_row = Project(
            user_id=user_id,
            name=request.name,
            max_cpu=request.max_cpu,
            max_memory=request.max_memory,
            max_disk=request.max_disk,
        )
        project = await self.uow.project.insert(project_row)
        await self.project_resource_client.create()
        return project
