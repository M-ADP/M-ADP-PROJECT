from fastapi import Depends

from src.core.domain.dns import DNS, DNSState
from src.app.dns.schemas import DNSCreate
from src.app.dns.exceptions import DNSNameAlreadyExists, ProjectAlreadyHasDNS
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client

DNS_DOMAIN = "mdeveloper.platform"


class CreateDNSForProjectUseCase(BaseUseCase):
    """프로젝트에 DNS를 생성하는 유즈케이스"""

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
        request: DNSCreate,
        user_id: int,
    ) -> DNS:
        async with self.uow:
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
