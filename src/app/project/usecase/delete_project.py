from src.app.project.exceptions import ProjectNotFound
from src.app.project.model import Project
from src.core.usecase import BaseUseCase


class DeleteProjectUseCase(BaseUseCase):
    """프로젝트를 삭제하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        user_id: str,
    ) -> Project:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        await self.project_resource_client.delete()
        await self.uow.project.delete(project)
        return project
