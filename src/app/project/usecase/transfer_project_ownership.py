from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.app.project.exceptions import (
    CannotTransferOwnershipToSelf,
    MemberNotFound,
    OnlyOwnerCanTransferOwnership,
    OwnershipTransferTargetMustBeViewer,
    ProjectNotFound,
)
from src.core.domain.project import ProjectMember
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class TransferProjectOwnershipUseCase(BaseUseCase):
    """프로젝트 소유권을 다른 VIEWER 멤버에게 이전하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

    async def __call__(
        self,
        project_id: str,
        target_user_id: str,
        user_id: str,
    ) -> ProjectMember:
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

            if target_member.role != "VIEWER":
                raise OwnershipTransferTargetMustBeViewer()

            await self.uow.project_member.update_role(
                project_id=project_id,
                user_id=user_id,
                role="VIEWER",
            )
            new_owner = await self.uow.project_member.update_role(
                project_id=project_id,
                user_id=target_user_id,
                role="OWNER",
            )

            if new_owner is None:
                raise MemberNotFound()
            return new_owner
