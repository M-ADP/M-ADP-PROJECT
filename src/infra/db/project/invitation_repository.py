from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.project import ProjectInvitation
from src.core.repository.project_invitation_repository import ProjectInvitationRepository
from src.infra.db.project.model import ProjectInvitation as ProjectInvitationModel


class ProjectInvitationRepositoryImpl(ProjectInvitationRepository):
    """프로젝트 초대 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_pending_by_project_and_user(
        self,
        project_id: int,
        invitee_user_id: int,
    ) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationModel).where(
            ProjectInvitationModel.project_id == project_id,
            ProjectInvitationModel.invitee_user_id == invitee_user_id,
            ProjectInvitationModel.status == "PENDING",
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def get_pending_by_token_hash(
        self,
        project_id: int,
        token_hash: str,
    ) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationModel).where(
            ProjectInvitationModel.project_id == project_id,
            ProjectInvitationModel.token_hash == token_hash,
            ProjectInvitationModel.status == "PENDING",
        ).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def get_by_id(
        self,
        project_id: int,
        invitation_id: int,
    ) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationModel).where(
            ProjectInvitationModel.project_id == project_id,
            ProjectInvitationModel.id == invitation_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def list_by_project(
        self,
        project_id: int,
        status: str | None,
        limit: int,
        cursor: int | None = None,
    ) -> list[ProjectInvitation]:
        conditions = [ProjectInvitationModel.project_id == project_id]
        if status is not None:
            conditions.append(ProjectInvitationModel.status == status)
        if cursor is not None:
            conditions.append(ProjectInvitationModel.id > cursor)

        stmt = (
            select(ProjectInvitationModel)
            .where(*conditions)
            .order_by(ProjectInvitationModel.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [model.to_entity() for model in result.scalars().all()]

    async def insert(self, invitation: ProjectInvitation) -> ProjectInvitation:
        model = ProjectInvitationModel(
            id=invitation.id,
            project_id=invitation.project_id,
            inviter_user_id=invitation.inviter_user_id,
            invitee_user_id=invitation.invitee_user_id,
            invitee_email=invitation.invitee_email,
            token_hash=invitation.token_hash,
            status=invitation.status,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,
            responded_at=invitation.responded_at,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def update_status(
        self,
        invitation_id: int,
        status: str,
    ) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationModel).where(
            ProjectInvitationModel.id == invitation_id,
            ProjectInvitationModel.status == "PENDING",
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.status = status
        model.responded_at = datetime.now()
        await self._session.flush()
        return model.to_entity()

    async def rotate_token(
        self,
        invitation_id: int,
        token_hash: str,
        expires_at,
    ) -> ProjectInvitation | None:
        stmt = select(ProjectInvitationModel).where(
            ProjectInvitationModel.id == invitation_id,
            ProjectInvitationModel.status == "PENDING",
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.token_hash = token_hash
        model.expires_at = expires_at
        await self._session.flush()
        return model.to_entity()
