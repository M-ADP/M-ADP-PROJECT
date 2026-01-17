from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS
from src.app.dns.schemas import DNSUpdate
from src.app.dns.exceptions import DNSNameAlreadyExists, DNSNotFound
from src.app.dns import repository as dns_repository
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound

DNS_DOMAIN = "mdeveloper.platform"


class UpdateDNSForProjectUseCase:
    """프로젝트의 DNS 서브도메인을 업데이트하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        dns_id: str,
        request: DNSUpdate,
        user_id: str,
        session: AsyncSession,
    ) -> DNS:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await dns_repository.get_by_id_for_project(session, dns_id, project_id)
        if dns is None:
            raise DNSNotFound()

        # 새 DNS 이름 생성
        new_dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

        # DNS 이름 중복 체크 (현재 DNS ID 제외)
        if await dns_repository.exists_by_dns_name(session, new_dns_name, exclude_dns_id=dns_id):
            raise DNSNameAlreadyExists()

        # DNS 이름 업데이트
        dns.dns_name = new_dns_name
        await session.flush()

        return dns
