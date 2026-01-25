from src.app.project.exceptions import (
    ProjectNotFound,
    MemberAlreadyExists,
    OnlyOwnerCanAddMembers,
    UserNotFound,
)
from src.app.project.model import ProjectMember
from src.app.project.schemas import ProjectMemberAdd
from src.core.usecase import BaseUseCase


class AddProjectMemberUseCase(BaseUseCase):
    """프로젝트에 멤버를 추가하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        request: ProjectMemberAdd,
        user_id: str,
    ) -> ProjectMember:
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
            username=user_info.username,
            profile_image=user_info.profile_image,
            role="VIEWER",
        )

        return await self.uow.project_member.insert(member)
