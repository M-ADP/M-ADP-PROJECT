import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    MemberAlreadyExists,
    MemberInvitationAlreadyExists,
    OnlyOwnerCanAddMembers,
    ProjectNotFound,
    UserEmailNotFound,
    UserNotFound,
)
from src.app.project.invitation_security import hash_invitation_token
from src.app.project.schemas import (
    ProjectMemberInvitationResponse,
    ProjectMemberInvite,
)
from src.common.config.gmail import get_gmail_config
from src.core.client.email import ProjectInvitationEmailClient
from src.core.client.user import UserClient
from src.core.domain.project import ProjectInvitation
from src.core.uow import UnitOfWork
from src.dependencies.client.email import get_project_invitation_email_client
from src.dependencies.client.user import get_user_client
from src.dependencies.uow import get_uow


class InviteProjectMemberUseCase(BaseUseCase):
    """프로젝트 멤버 초대를 생성하고 메일을 발송하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        user_client: UserClient = Depends(get_user_client),
        email_client: ProjectInvitationEmailClient = Depends(
            get_project_invitation_email_client
        ),
    ):
        self.uow = uow
        self.user_client = user_client
        self.email_client = email_client

    async def __call__(
        self,
        project_id: int,
        request: ProjectMemberInvite,
        user_id: int,
    ) -> ProjectMemberInvitationResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanAddMembers()

            exists = await self.uow.project_member.exists_by_project_and_user(
                project_id,
                request.user_id,
            )
            if exists:
                raise MemberAlreadyExists()

            user_info = await self.user_client.get_user(request.user_id)
            if user_info is None:
                raise UserNotFound()

            pending = await self.uow.project_invitation.get_pending_by_project_and_user(
                project_id,
                request.user_id,
            )
            if pending is not None:
                raise MemberInvitationAlreadyExists()

            if user_info.email is None:
                raise UserEmailNotFound()

            token = secrets.token_urlsafe(32)
            config = get_gmail_config()
            now = datetime.now(timezone.utc)
            invitation = ProjectInvitation(
                project_id=project_id,
                inviter_user_id=user_id,
                invitee_user_id=request.user_id,
                invitee_email=user_info.email,
                token_hash=hash_invitation_token(token),
                status="PENDING",
                created_at=now,
                expires_at=now + timedelta(hours=config.invitation_ttl_hours),
            )
            saved = await self.uow.project_invitation.insert(invitation)

            await self.email_client.send_project_invitation(
                to_email=saved.invitee_email,
                project_name=project.name,
                inviter_user_id=user_id,
                invite_url=self._build_accept_url(project_id, token),
            )

            return ProjectMemberInvitationResponse.model_validate(saved)

    def _build_accept_url(self, project_id: int, token: str) -> str:
        config = get_gmail_config()
        return (
            f"{config.public_base_url.rstrip('/')}"
            f"/projects/{project_id}/member-invitations/{token}/accept"
        )
