from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS
from src.app.dns import repository as dns_repository
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound


class GetDNSForProjectUseCase:
    """프로젝트의 DNS를 조회하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> DNS | None:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await dns_repository.get_by_project(session, project_id)
        return dns
