from fastapi import Depends

from src.app.project.exceptions import (
    ProjectNotFound,
    MemberNotFound,
    CannotRemoveOwner,
    OnlyOwnerCanRemoveMembers,
)
from src.core.domain.project import ProjectMember
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class RemoveProjectMemberUseCase(BaseUseCase):
    """프로젝트에서 멤버를 제거하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

    async def __call__(
        self,
        project_id: str,
        target_user_id: str,
        user_id: str,
    ) -> ProjectMember:
        async with self.uow:
            # 프로젝트 존재 여부 확인
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            # 요청자가 프로젝트 소유자인지 확인
            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanRemoveMembers()

            # 대상 멤버 조회
            member = await self.uow.project_member.get_by_project_and_user(
                project_id, target_user_id
            )
            if member is None:
                raise MemberNotFound()

            # 소유자는 제거 불가
            if member.role == "OWNER":
                raise CannotRemoveOwner()

            await self.uow.project_member.delete(member)
            return member
