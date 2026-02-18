from fastapi import Depends

from src.app.project.exceptions import (
    ProjectNotFound,
    InvalidPassword,
    OnlyOwnerCanDeleteProject,
)
from src.core.domain.project import Project
from src.app.project.schemas import ProjectDelete
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.core.client.user import UserClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client
from src.dependencies.client.user import get_user_client


class DeleteProjectUseCase(BaseUseCase):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
        user_client: UserClient = Depends(get_user_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client
        self.user_client = user_client

    async def __call__(
        self,
        project_id: str,
        request: ProjectDelete,
        user_id: str,
    ) -> Project:
        async with self.uow:
            is_valid = await self.user_client.verify_password(user_id, request.password)
            if not is_valid:
                raise InvalidPassword()

            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanDeleteProject()

            await self.project_resource_client.delete(
                user_id=user_id,
                project=project,
            )
            await self.uow.project.delete(project)
            return project
