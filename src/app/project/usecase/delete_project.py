from src.app.project.exceptions import ProjectNotFound, InvalidPassword
from src.app.project.model import Project
from src.app.project.schemas import ProjectDelete
from src.core.usecase import BaseUseCase


class DeleteProjectUseCase(BaseUseCase):
    async def execute(
        self,
        project_id: str,
        request: ProjectDelete,
        user_id: str,
    ) -> Project:
        is_valid = await self.user_client.verify_password(user_id, request.password)
        if not is_valid:
            raise InvalidPassword()

        project = await self.uow.project.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound()

        if project.user_id != user_id:
            raise InvalidPassword()

        await self.project_resource_client.delete()
        await self.uow.project.delete(project)
        return project
