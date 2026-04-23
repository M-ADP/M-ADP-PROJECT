import logging

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

logger = logging.getLogger(__name__)


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
                logger.info(
                    "project invitation cancel failed: project not found project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                logger.info(
                    "project invitation cancel denied: requester is not owner project_id=%s requester_user_id=%s invitation_id=%s",
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
                    "project invitation cancel failed: invitation not found project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise InvitationNotFound()
            if invitation.status != "PENDING":
                logger.info(
                    "project invitation cancel denied: invitation is not pending project_id=%s requester_user_id=%s invitation_id=%s status=%s",
                    project_id,
                    user_id,
                    invitation_id,
                    invitation.status,
                )
                raise CannotCancelInvitation()

            canceled = await self.uow.project_invitation.update_status(
                invitation_id,
                "CANCELED",
            )
            if canceled is None:
                logger.info(
                    "project invitation cancel failed: pending status update failed project_id=%s requester_user_id=%s invitation_id=%s",
                    project_id,
                    user_id,
                    invitation_id,
                )
                raise CannotCancelInvitation()

            logger.info(
                "project invitation canceled: project_id=%s invitation_id=%s requester_user_id=%s invitee_user_id=%s",
                project_id,
                invitation_id,
                user_id,
                canceled.invitee_user_id,
            )
            return ProjectMemberInvitationResponse.model_validate(canceled)
