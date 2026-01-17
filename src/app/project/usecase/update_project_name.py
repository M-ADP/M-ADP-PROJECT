from fastapi import Depends

from src.app.project.schemas import ProjectNameUpdate
from src.app.project.exceptions import (
    ProjectNameAlreadyExists,
    ProjectNotFound,
)
from src.app.project.models import Project
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class UpdateProjectNameUseCase(BaseUseCase):
    """프로젝트 이름을 업데이트하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        request: ProjectNameUpdate,
        user_id: str,
    ) -> Project:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        if await self.uow.project.exists_by_name(
            user_id,
            request.name,
            exclude_project_id=project_id,
        ):
            raise ProjectNameAlreadyExists()

        project.update_name(request.name)
        return project
