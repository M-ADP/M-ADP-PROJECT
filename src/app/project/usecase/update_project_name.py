from src.app.project.schemas import ProjectNameUpdate
from src.app.project.exceptions import (
    ProjectNameAlreadyExists,
    ProjectNotFound,
    OnlyOwnerCanUpdateProjectName,
)
from src.app.project.model import Project
from src.core.usecase import BaseUseCase


class UpdateProjectNameUseCase(BaseUseCase):
    """프로젝트 이름을 업데이트하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        request: ProjectNameUpdate,
        user_id: str,
    ) -> Project:
        project = await self.uow.project.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound()

        is_owner = await self.uow.project_member.is_owner(project_id, user_id)
        if not is_owner:
            raise OnlyOwnerCanUpdateProjectName()

        if await self.uow.project.exists_by_name(
            user_id,
            request.name,
            exclude_project_id=project_id,
        ):
            raise ProjectNameAlreadyExists()

        return await self.uow.project.update_name(project_id, request.name)
