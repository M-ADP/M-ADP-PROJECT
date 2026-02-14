from src.app.project.schemas import ProjectCreate
from src.app.project.exceptions import (
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
)
from src.app.project.model import Project, ProjectMember
from src.core.usecase import BaseUseCase

PROJECT_LIMIT = 3
# 이거 config로 뭉쳐서 환경변수로 하는게 나을 듯


class CreateProjectUseCase(BaseUseCase):
    """프로젝트를 생성하는 유즈케이스"""

    async def execute(
        self,
        request: ProjectCreate,
        user_id: str,
    ) -> Project:
        project_count = await self.uow.project.count_by_user(user_id)
        if project_count >= PROJECT_LIMIT:
            raise ProjectLimitExceeded()

        if await self.uow.project.exists_by_name(user_id, request.name):
            raise ProjectNameAlreadyExists()

        project_row = Project(
            user_id=user_id,
            name=request.name,
            max_cpu=request.max_cpu,
            max_memory=request.max_memory,
            max_disk=request.max_disk,
        )
        project = await self.uow.project.insert(project_row)

        # 프로젝트 생성자를 OWNER로 자동 추가
        owner_member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            username=user_id,  # TODO: 실제 환경에서는 사용자 서비스에서 조회
            profile_image=None,
            role="OWNER",
        )
        await self.uow.project_member.insert(owner_member)

        await self.project_resource_client.create(
            user_id=user_id,
            project_id=project.id,
            project=request
        )
        return project
