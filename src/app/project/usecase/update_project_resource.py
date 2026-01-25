from src.app.project.exceptions import ProjectNotFound, DiskCannotBeReduced
from src.app.project.model import Project
from src.app.project.schemas import ProjectResourceUpdate
from src.core.usecase import BaseUseCase


class UpdateProjectResourceUseCase(BaseUseCase):
    async def execute(
        self,
        project_id: str,
        request: ProjectResourceUpdate,
        user_id: str,
    ) -> Project:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        if request.max_disk is not None and request.max_disk < project.max_disk:
            raise DiskCannotBeReduced()

        project = await self.uow.project.update_resource(
            project_id=project_id,
            max_cpu=request.max_cpu,
            max_memory=request.max_memory,
            max_disk=request.max_disk
        )
        await self.project_resource_client.allocate()
        return project
