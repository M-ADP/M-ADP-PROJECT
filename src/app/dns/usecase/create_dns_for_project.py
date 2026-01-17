from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS, DNSState
from src.app.dns.schemas import DNSCreate
from src.app.dns.exceptions import DNSNameAlreadyExists, ProjectAlreadyHasDNS
from src.app.dns import repository as dns_repository
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound
from src.common.id_generator import generate_sonyflake_id

DNS_DOMAIN = "mdeveloper.platform"


class CreateDNSForProjectUseCase:
    """프로젝트에 DNS를 생성하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        request: DNSCreate,
        user_id: str,
        session: AsyncSession,
    ) -> DNS:
        # 프로젝트 확인
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        # 프로젝트에 이미 DNS가 있는지 확인
        if await dns_repository.exists_by_project(session, project_id):
            raise ProjectAlreadyHasDNS()

        # DNS 이름 생성
        dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

        # DNS 이름 중복 체크
        if await dns_repository.exists_by_dns_name(session, dns_name):
            raise DNSNameAlreadyExists()

        # 새 DNS 생성
        dns_id = generate_sonyflake_id()
        dns = DNS(
            id=dns_id,
            project_id=project_id,
            dns_name=dns_name,
            state=DNSState.PENDING,
        )
        dns = await dns_repository.insert(session, dns)

        return dns
