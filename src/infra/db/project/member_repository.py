from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.project import ProjectMember
from src.core.repository.project_member_repository import ProjectMemberRepository
from src.infra.db.project.model import ProjectMember as ProjectMemberModel


class ProjectMemberRepositoryImpl(ProjectMemberRepository):
    """프로젝트 멤버 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @staticmethod
    def _normalize_role(role: str) -> str:
        return "OWNER" if role == "OWNER" else "MEMBER"

    async def list_by_project(
        self,
        project_id: int,
        limit: int,
        cursor: int | None = None,
    ) -> list[ProjectMember]:
        """프로젝트의 멤버 목록을 조회합니다."""
        conditions = [ProjectMemberModel.project_id == project_id]
        if cursor:
            conditions.append(ProjectMemberModel.id > cursor)

        stmt = (
            select(ProjectMemberModel)
            .where(*conditions)
            .order_by(ProjectMemberModel.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def get_by_project_and_user(
        self,
        project_id: int,
        user_id: str,
    ) -> ProjectMember | None:
        """프로젝트와 사용자 ID로 멤버를 조회합니다."""
        stmt = select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def exists_by_project_and_user(
        self,
        project_id: int,
        user_id: str,
    ) -> bool:
        """프로젝트에 해당 사용자가 멤버로 존재하는지 확인합니다."""
        stmt = (
            select(ProjectMemberModel.id)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def insert(self, member: ProjectMember) -> ProjectMember:
        """멤버를 추가합니다."""
        model = ProjectMemberModel(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role=member.role,
            joined_at=member.joined_at,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def delete(self, member: ProjectMember) -> None:
        """멤버를 삭제합니다."""
        model = await self._session.get(ProjectMemberModel, member.id)
        if model is None:
            return
        await self._session.delete(model)
        await self._session.flush()

    async def is_owner(self, project_id: int, user_id: str) -> bool:
        """사용자가 프로젝트 소유자인지 확인합니다."""
        stmt = (
            select(ProjectMemberModel.id)
            .where(
                ProjectMemberModel.project_id == project_id,
                ProjectMemberModel.user_id == user_id,
                ProjectMemberModel.role == "OWNER",
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def has_access(self, project_id: int, user_id: str) -> bool:
        """사용자가 프로젝트에 접근 권한이 있는지 확인합니다."""
        return await self.exists_by_project_and_user(project_id, user_id)

    async def list_project_ids_by_user(
        self,
        user_id: str,
        limit: int,
        cursor: int | None = None,
    ) -> list[int]:
        """사용자가 참여한 프로젝트 ID 목록을 조회합니다."""
        conditions = [ProjectMemberModel.user_id == user_id]
        if cursor is not None:
            conditions.append(ProjectMemberModel.project_id > cursor)

        stmt = (
            select(ProjectMemberModel.project_id)
            .where(*conditions)
            .order_by(ProjectMemberModel.project_id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_role(self, project_id: int, user_id: str) -> str | None:
        """프로젝트에서 사용자의 역할을 조회합니다."""
        stmt = select(ProjectMemberModel.role).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()
        if role is None:
            return None
        return self._normalize_role(role)

    async def get_roles_batch(
        self,
        project_ids: list[int],
        user_id: str,
    ) -> dict[int, str]:
        """여러 프로젝트에서 사용자의 역할을 일괄 조회합니다."""
        if not project_ids:
            return {}

        stmt = select(
            ProjectMemberModel.project_id,
            ProjectMemberModel.role,
        ).where(
            ProjectMemberModel.project_id.in_(project_ids),
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return {
            row.project_id: self._normalize_role(row.role)
            for row in result.all()
        }

    async def update_role(
        self,
        project_id: int,
        user_id: str,
        role: str,
    ) -> ProjectMember | None:
        """프로젝트 멤버 역할을 변경합니다."""
        stmt = select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.role = role
        await self._session.flush()
        return model.to_entity()
