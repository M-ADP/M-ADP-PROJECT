from src.app.dns.model import DNS, DNSState
from src.app.dns.schemas import DNSCreate
from src.app.dns.exceptions import DNSNameAlreadyExists, ProjectAlreadyHasDNS
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.core.usecase import BaseUseCase

DNS_DOMAIN = "mdeveloper.platform"


class CreateDNSForProjectUseCase(BaseUseCase):
    """프로젝트에 DNS를 생성하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        request: DNSCreate,
        user_id: str,
    ) -> DNS:
        # 프로젝트 확인
        project = await self.uow.project.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound()

        is_owner = await self.uow.project_member.is_owner(project_id, user_id)
        if not is_owner:
            raise OnlyOwnerCanManageDNS()

        # 프로젝트에 이미 DNS가 있는지 확인
        if await self.uow.dns.exists_by_project(project_id):
            raise ProjectAlreadyHasDNS()

        # DNS 이름 생성
        dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

        # DNS 이름 중복 체크
        if await self.uow.dns.exists_by_dns_name(dns_name):
            raise DNSNameAlreadyExists()

        # 새 DNS 생성
        dns = DNS(
            project_id=project_id,
            dns_name=dns_name,
            state=DNSState.PENDING,
        )
        dns = await self.uow.dns.insert(dns)
        await self.project_resource_client.create_dns()
        return dns
