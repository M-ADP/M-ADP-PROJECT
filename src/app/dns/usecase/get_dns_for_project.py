from src.app.dns.model import DNS
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase


class GetDNSForProjectUseCase(BaseUseCase):
    """프로젝트의 DNS를 조회하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        user_id: str,
    ) -> DNS | None:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await self.uow.dns.get_by_project(project_id)
        return dns
