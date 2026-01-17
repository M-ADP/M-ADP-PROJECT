from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS
from src.app.dns.exceptions import DNSNotFound
from src.app.dns import repository as dns_repository
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound


class DeleteDNSFromProjectUseCase:
    """프로젝트의 DNS를 삭제하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        dns_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> DNS:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await dns_repository.get_by_id_for_project(session, dns_id, project_id)
        if dns is None:
            raise DNSNotFound()

        # DNS 삭제
        await dns_repository.delete(session, dns)

        return dns
