from fastapi import Depends

from src.app.project.exceptions import (
    ProjectNotFound,
    OnlyOwnerCanDeleteProject,
    ProjectDeletionFailed,
)
from src.core.exceptions import ResourceServerException
from src.core.domain.project import Project
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class DeleteProjectUseCase(BaseUseCase):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> Project:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanDeleteProject()

            try:
                await self.project_resource_client.delete(
                    user_id=user_id,
                    role=role,
                    project=project,
                )
            except ResourceServerException as e:
                raise ProjectDeletionFailed() from e
            await self.uow.project.delete(project)
            return project
