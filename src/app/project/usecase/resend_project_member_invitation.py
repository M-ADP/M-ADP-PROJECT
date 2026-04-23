import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    CannotResendInvitation,
    InvitationNotFound,
    OnlyOwnerCanAddMembers,
    ProjectNotFound,
)
from src.app.project.invitation_security import hash_invitation_token
from src.app.project.schemas import ProjectMemberInvitationResponse
from src.common.config.gmail import get_gmail_config
from src.core.client.email import ProjectInvitationEmailClient
from src.core.uow import UnitOfWork
from src.dependencies.client.email import get_project_invitation_email_client
from src.dependencies.uow import get_uow

logger = logging.getLogger(__name__)


class ResendProjectMemberInvitationUseCase(BaseUseCase):
    """프로젝트 초대 메일을 재발송하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        email_client: ProjectInvitationEmailClient = Depends(
            get_project_invitation_email_client
        ),
    ):
        self.uow = uow
        self.email_client = email_client

    async def __call__(
        self,
        project_id: int,
        invitation_id: int,
        user_id: int,
    ) -> ProjectMemberInvitationResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                logger.info(
                    "project invitation resend failed: project not found project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                logger.info(
                    "project invitation resend denied: requester is not owner project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise OnlyOwnerCanAddMembers()

            invitation = await self.uow.project_invitation.get_by_id(
                project_id,
                invitation_id,
            )
            if invitation is None:
                logger.info(
                    "project invitation resend failed: invitation not found project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise InvitationNotFound()
            if invitation.status != "PENDING":
                logger.info(
                    "project invitation resend denied: invitation is not pending project_id=%s requester_user_id=%s invitation_id=%s status=%s",
                    project_id,
                    user_id,
                    invitation_id,
                    invitation.status,
                )
                raise CannotResendInvitation()

            token = secrets.token_urlsafe(32)
            config = get_gmail_config()
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=config.invitation_ttl_hours
            )
            updated = await self.uow.project_invitation.rotate_token(
                invitation_id,
                hash_invitation_token(token),
                expires_at,
            )
            if updated is None:
                logger.info(
                    "project invitation resend failed: token rotation failed project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise CannotResendInvitation()
            logger.info(
                "project invitation token rotated: project_id=%s invitation_id=%s requester_user_id=%s invitee_user_id=%s expires_at=%s",
                project_id,
                invitation_id,
                user_id,
                updated.invitee_user_id,
                updated.expires_at.isoformat(),
            )

            await self.email_client.send_project_invitation(
                to_email=updated.invitee_email,
                project_name=project.name,
                inviter_user_id=user_id,
                invite_url=self._build_invitation_url(project_id, token),
            )
            logger.info(
                "project invitation email resent: project_id=%s invitation_id=%s requester_user_id=%s invitee_user_id=%s invitee_email=%s",
                project_id,
                invitation_id,
                user_id,
                updated.invitee_user_id,
                updated.invitee_email,
            )

            return ProjectMemberInvitationResponse.model_validate(updated)

    def _build_invitation_url(self, project_id: int, token: str) -> str:
        config = get_gmail_config()
        return (
            f"{config.frontend_base_url.rstrip('/')}"
            f"/projects/{project_id}/member-invitations/{token}"
        )
