from fastapi import Depends

from src.core.domain.dns import DNS
from src.app.dns.exceptions import DNSNotFound
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class DeleteDNSFromProjectUseCase(BaseUseCase):
    """프로젝트의 DNS를 삭제하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(
        self,
        project_id: str,
        dns_id: str,
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

            # DNS 삭제
            await self.project_resource_client.delete_dns()
            await self.uow.dns.delete(dns)

            return dns
