from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.exceptions import ProjectNotFound
from src.app.project.models import Project
from src.app.project import repository


class DeleteProjectUseCase:
    """프로젝트를 삭제하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> Project:
        project = await repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        await repository.delete(session, project)
        return project
