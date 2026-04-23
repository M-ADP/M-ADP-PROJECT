from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import OnlyOwnerCanAddMembers, ProjectNotFound
from src.app.project.schemas import ProjectMemberInvitationResponse
from src.common.schemas import CursorPage
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class ListProjectMemberInvitationsUseCase(BaseUseCase):
    """프로젝트 초대 목록을 조회하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

    async def __call__(
        self,
        project_id: int,
        user_id: int,
        status: str | None = "PENDING",
        limit: int = 20,
        cursor: int | None = None,
    ) -> CursorPage[ProjectMemberInvitationResponse]:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanAddMembers()

            invitations = await self.uow.project_invitation.list_by_project(
                project_id=project_id,
                status=status,
                limit=limit + 1,
                cursor=cursor,
            )
            has_next = len(invitations) > limit
            if has_next:
                invitations = invitations[:limit]

            return CursorPage(
                items=[
                    ProjectMemberInvitationResponse.model_validate(invitation)
                    for invitation in invitations
                ],
                has_next=has_next,
            )
