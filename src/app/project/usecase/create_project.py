from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.schemas import ProjectCreate
from src.app.project.exceptions import (
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
)
from src.app.project.models import Project
from src.app.project import repository
from src.common.id_generator import generate_sonyflake_id

PROJECT_LIMIT = 3

class CreateProjectUseCase:
    """프로젝트를 생성하는 유즈케이스"""

    async def __call__(
        self,
        request: ProjectCreate,
        user_id: str,
        session: AsyncSession,
    ) -> Project:
        project_count = await repository.count_by_user(session, user_id)
        if project_count >= PROJECT_LIMIT:
            raise ProjectLimitExceeded()

        if await repository.exists_by_name(session, user_id, request.name):
            raise ProjectNameAlreadyExists()

        project_id = generate_sonyflake_id()
        project_row = Project(
            id=project_id,
            user_id=user_id,
            name=request.name,
            max_cpu=request.max_cpu,
            max_memory=request.max_memory,
            max_disk=request.max_disk,
        )
        return await repository.insert(session, project_row)
