from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.schemas import ProjectNameUpdate
from src.app.project.exceptions import (
    ProjectNameAlreadyExists,
    ProjectNotFound,
)
from src.app.project.models import Project
from src.app.project import repository


class UpdateProjectNameUseCase:
    """프로젝트 이름을 업데이트하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        request: ProjectNameUpdate,
        user_id: str,
        session: AsyncSession,
    ) -> Project:
        project = await repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        if await repository.exists_by_name(
            session,
            user_id,
            request.name,
            exclude_project_id=project_id,
        ):
            raise ProjectNameAlreadyExists()

        project.update_name(request.name)
        await session.flush()
        return project
