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
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanAddMembers()

            invitation = await self.uow.project_invitation.get_by_id(
                project_id,
                invitation_id,
            )
            if invitation is None:
                raise InvitationNotFound()
            if invitation.status != "PENDING":
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
                raise CannotResendInvitation()

            await self.email_client.send_project_invitation(
                to_email=updated.invitee_email,
                project_name=project.name,
                inviter_user_id=user_id,
                invite_url=self._build_accept_url(project_id, token),
            )

            return ProjectMemberInvitationResponse.model_validate(updated)

    def _build_accept_url(self, project_id: int, token: str) -> str:
        config = get_gmail_config()
        return (
            f"{config.public_base_url.rstrip('/')}"
            f"/projects/{project_id}/member-invitations/{token}/accept"
        )
