from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    CannotCancelInvitation,
    InvitationNotFound,
    OnlyOwnerCanAddMembers,
    ProjectNotFound,
)
from src.app.project.schemas import ProjectMemberInvitationResponse
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class CancelProjectMemberInvitationUseCase(BaseUseCase):
    """프로젝트 초대를 취소하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

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
                raise CannotCancelInvitation()

            canceled = await self.uow.project_invitation.update_status(
                invitation_id,
                "CANCELED",
            )
            if canceled is None:
                raise CannotCancelInvitation()

            return ProjectMemberInvitationResponse.model_validate(canceled)
