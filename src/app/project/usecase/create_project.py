from fastapi import Depends

from src.app.project.schemas import ProjectCreate
from src.app.project.exceptions import (
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
)
from src.core.domain.project import Project, ProjectMember
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client

PROJECT_LIMIT = 3
# 이거 config로 뭉쳐서 환경변수로 하는게 나을 듯


class CreateProjectUseCase(BaseUseCase):
    """프로젝트를 생성하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(
        self,
        request: ProjectCreate,
        user_id: int,
        role: str,
    ) -> Project:
        async with self.uow:
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
                role="OWNER",
            )
            await self.uow.project_member.insert(owner_member)

            await self.project_resource_client.create(
                user_id=user_id,
                role=role,
                project=project,
            )
            return project
