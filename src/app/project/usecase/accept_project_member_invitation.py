import logging
from datetime import datetime, timezone

from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    InvitationExpired,
    InvitationNotFound,
    InvitationTargetMismatch,
    MemberAlreadyExists,
    ProjectNotFound,
    UserNotFound,
)
from src.app.project.invitation_security import hash_invitation_token
from src.app.project.schemas import ProjectMemberResponse
from src.core.client.user import UserClient
from src.core.domain.project import ProjectMember
from src.core.uow import UnitOfWork
from src.dependencies.client.user import get_user_client
from src.dependencies.uow import get_uow

logger = logging.getLogger(__name__)


class AcceptProjectMemberInvitationUseCase(BaseUseCase):
    """프로젝트 멤버 초대를 승인하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        user_client: UserClient = Depends(get_user_client),
    ):
        self.uow = uow
        self.user_client = user_client

    async def __call__(
        self,
        project_id: int,
        token: str,
        user_id: int,
    ) -> ProjectMemberResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                logger.info(
                    "project invitation accept failed: project not found project_id=%s requester_user_id=%s",
                    project_id,
                    user_id,
                )
                raise ProjectNotFound()

            invitation = await self.uow.project_invitation.get_pending_by_token_hash(
                project_id,
                hash_invitation_token(token),
            )
            if invitation is None:
                logger.info(
                    "project invitation accept failed: pending invitation not found project_id=%s requester_user_id=%s",
                    project_id,
                    user_id,
                )
                raise InvitationNotFound()

            if self._as_utc(invitation.expires_at) <= datetime.now(timezone.utc):
                await self.uow.project_invitation.update_status(
                    invitation.id,
                    "EXPIRED",
                )
                logger.info(
                    "project invitation accept failed: invitation expired project_id=%s invitation_id=%s requester_user_id=%s invitee_user_id=%s expires_at=%s",
                    project_id,
                    invitation.id,
                    user_id,
                    invitation.invitee_user_id,
                    invitation.expires_at.isoformat(),
                )
                raise InvitationExpired()

            if invitation.invitee_user_id != user_id:
                logger.info(
                    "project invitation accept denied: requester is not invitee project_id=%s invitation_id=%s requester_user_id=%s invitee_user_id=%s",
                    project_id,
                    invitation.id,
                    user_id,
                    invitation.invitee_user_id,
                )
                raise InvitationTargetMismatch()

            exists = await self.uow.project_member.exists_by_project_and_user(
                project_id,
                user_id,
            )
            if exists:
                logger.info(
                    "project invitation accept skipped: user already member project_id=%s invitation_id=%s requester_user_id=%s",
                    project_id,
                    invitation.id,
                    user_id,
                )
                raise MemberAlreadyExists()

            user_info = await self.user_client.get_user(user_id)
            if user_info is None:
                logger.info(
                    "project invitation accept failed: user not found project_id=%s invitation_id=%s requester_user_id=%s",
                    project_id,
                    invitation.id,
                    user_id,
                )
                raise UserNotFound()

            member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                role="MEMBER",
            )
            saved = await self.uow.project_member.insert(member)
            await self.uow.project_invitation.update_status(
                invitation.id,
                "ACCEPTED",
            )
            logger.info(
                "project invitation accepted: project_id=%s invitation_id=%s user_id=%s member_id=%s",
                project_id,
                invitation.id,
                user_id,
                saved.id,
            )

            return ProjectMemberResponse(
                user_id=saved.user_id,
                username=user_info.username,
                profile_image=user_info.profile_image,
                role=saved.role,
                joined_at=saved.joined_at,
            )

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
