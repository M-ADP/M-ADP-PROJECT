from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.models import Project
from src.core.repository.project_repository import ProjectRepository


class ProjectRepositoryImpl(ProjectRepository):
    """프로젝트 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count_by_user(self, user_id: str) -> int:
        """사용자의 프로젝트 개수를 조회합니다."""
        stmt = select(func.count()).select_from(Project).where(Project.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def exists_by_name(
        self,
        user_id: str,
        name: str,
        exclude_project_id: str | None = None,
    ) -> bool:
        """프로젝트 이름 중복 여부를 확인합니다."""
        conditions = [
            Project.user_id == user_id,
            func.lower(Project.name) == func.lower(name),
        ]
        if exclude_project_id:
            conditions.append(Project.id != exclude_project_id)

        stmt = select(Project.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def get_by_id_for_user(
        self, project_id: str, user_id: str
    ) -> Project | None:
        """사용자의 프로젝트를 ID로 조회합니다."""
        stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, project: Project) -> Project:
        """프로젝트를 삽입합니다."""
        self._session.add(project)
        await self._session.flush()
        return project

    async def delete(self, project: Project) -> None:
        """프로젝트를 삭제합니다."""
        await self._session.delete(project)
        await self._session.flush()
