from fastapi import Depends

from src.app.project.exceptions import (
    ProjectNotFound,
    MemberAlreadyExists,
    OnlyOwnerCanAddMembers,
    UserNotFound,
)
from src.core.domain.project import ProjectMember
from src.app.project.schemas import ProjectMemberAdd, ProjectMemberResponse
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.user import UserClient
from src.dependencies.uow import get_uow
from src.dependencies.client.user import get_user_client


class AddProjectMemberUseCase(BaseUseCase):
    """프로젝트에 멤버를 추가하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        user_client: UserClient = Depends(get_user_client),
    ):
        self.uow = uow
        self.user_client = user_client

    async def __call__(
        self,
        project_id: str,
        request: ProjectMemberAdd,
        user_id: str,
    ) -> ProjectMemberResponse:
        async with self.uow:
            # 프로젝트 존재 여부 확인
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            # 요청자가 프로젝트 소유자인지 확인
            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanAddMembers()

            # 이미 멤버인지 확인
            exists = await self.uow.project_member.exists_by_project_and_user(
                project_id, request.user_id
            )
            if exists:
                raise MemberAlreadyExists()

            # 사용자 존재 여부 확인
            user_info = await self.user_client.get_user(request.user_id)
            if user_info is None:
                raise UserNotFound()

            member = ProjectMember(
                project_id=project_id,
                user_id=request.user_id,
                role="MEMBER",
            )
            saved = await self.uow.project_member.insert(member)
            return ProjectMemberResponse(
                user_id=saved.user_id,
                username=user_info.username,
                profile_image=user_info.profile_image,
                role=saved.role,
                joined_at=saved.joined_at,
            )
