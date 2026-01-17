from fastapi import Depends

from src.app.project.exceptions import ProjectNotFound
from src.app.project.models import Project
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class DeleteProjectUseCase(BaseUseCase):
    """프로젝트를 삭제하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        await self.uow.project.delete(project)
        return project
