from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    CannotTransferOwnershipToSelf,
    MemberNotFound,
    OnlyOwnerCanTransferOwnership,
    OwnershipTransferTargetMustBeMember,
    ProjectNotFound,
)
from src.app.project.schemas import ProjectMemberResponse
from src.core.uow import UnitOfWork
from src.core.client.user import UserClient
from src.dependencies.uow import get_uow
from src.dependencies.client.user import get_user_client


class TransferProjectOwnershipUseCase(BaseUseCase):
    """프로젝트 소유권을 다른 MEMBER 멤버에게 이전하는 유즈케이스"""

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
        target_user_id: str,
        user_id: str,
    ) -> ProjectMemberResponse:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            if target_user_id == user_id:
                raise CannotTransferOwnershipToSelf()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanTransferOwnership()

            target_member = await self.uow.project_member.get_by_project_and_user(
                project_id,
                target_user_id,
            )
            if target_member is None:
                raise MemberNotFound()

            if target_member.role != "MEMBER":
                raise OwnershipTransferTargetMustBeMember()

            await self.uow.project_member.update_role(
                project_id=project_id,
                user_id=user_id,
                role="MEMBER",
            )
            new_owner = await self.uow.project_member.update_role(
                project_id=project_id,
                user_id=target_user_id,
                role="OWNER",
            )

            if new_owner is None:
                raise MemberNotFound()

            user_info = await self.user_client.get_user(target_user_id)
            return ProjectMemberResponse(
                user_id=new_owner.user_id,
                username=user_info.username if user_info else target_user_id,
                profile_image=user_info.profile_image if user_info else None,
                role=new_owner.role,
                joined_at=new_owner.joined_at,
            )
