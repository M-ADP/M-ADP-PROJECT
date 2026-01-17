from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.model import Project
from src.core.repository.project_repository import ProjectRepository
from src.infra.db.project.model import Project as ProjectModel


class ProjectRepositoryImpl(ProjectRepository):
    """프로젝트 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count_by_user(self, user_id: str) -> int:
        """사용자의 프로젝트 개수를 조회합니다."""
        stmt = select(func.count()).select_from(ProjectModel).where(
            ProjectModel.user_id == user_id
        )
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
            ProjectModel.user_id == user_id,
            func.lower(ProjectModel.name) == func.lower(name),
        ]
        if exclude_project_id:
            conditions.append(ProjectModel.id != exclude_project_id)

        stmt = select(ProjectModel.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def get_by_id_for_user(
        self, project_id: str, user_id: str
    ) -> Project | None:
        """사용자의 프로젝트를 ID로 조회합니다."""
        stmt = select(ProjectModel).where(
            ProjectModel.id == project_id,
            ProjectModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def insert(self, project: Project) -> Project:
        """프로젝트를 삽입합니다."""
        model = ProjectModel(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            max_cpu=project.max_cpu,
            max_memory=project.max_memory,
            max_disk=project.max_disk,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def delete(self, project: Project) -> None:
        """프로젝트를 삭제합니다."""
        model = await self._session.get(ProjectModel, project.id)
        if model is None:
            return
        await self._session.delete(model)
        await self._session.flush()

    async def update_name(self, project_id: str, name: str) -> Project:
        """프로젝트 이름을 업데이트합니다."""
        model = await self._session.get(ProjectModel, project_id)
        if model is None:
            raise ValueError("Project not found")
        model.name = name
        await self._session.flush()
        return model.to_entity()
