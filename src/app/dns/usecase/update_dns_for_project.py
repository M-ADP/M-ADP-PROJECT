from fastapi import Depends

from src.core.domain.dns import DNS
from src.app.dns.schemas import DNSUpdate
from src.app.dns.exceptions import DNSNameAlreadyExists, DNSNotFound
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client

DNS_DOMAIN = "mdeveloper.platform"


class UpdateDNSForProjectUseCase(BaseUseCase):
    """프로젝트의 DNS 서브도메인을 업데이트하는 유즈케이스"""

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
        dns_id: int,
        request: DNSUpdate,
        user_id: str,
    ) -> DNS:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanManageDNS()

            dns = await self.uow.dns.get_by_id_for_project(dns_id, project_id)
            if dns is None:
                raise DNSNotFound()

            # 새 DNS 이름 생성
            new_dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

            # DNS 이름 중복 체크 (현재 DNS ID 제외)
            if await self.uow.dns.exists_by_dns_name(new_dns_name, exclude_dns_id=dns_id):
                raise DNSNameAlreadyExists()

            dns = await self.uow.dns.update_name(dns_id, project_id, new_dns_name)
            await self.project_resource_client.update_dns()
            return dns
