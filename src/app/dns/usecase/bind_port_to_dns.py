from fastapi import Depends

from src.core.domain.dns import DNS
from src.app.dns.schemas import DNSPortBinding
from src.app.dns.exceptions import DNSNotFound
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.app.port.exceptions import PortNotFound
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class BindPortToDNSUseCase(BaseUseCase):
    """DNS에 공개 포트를 바인딩하는 유즈케이스"""

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
        request: DNSPortBinding,
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

            # DNS 확인
            dns = await self.uow.dns.get_by_id_for_project(dns_id, project_id)
            if dns is None:
                raise DNSNotFound()

            # 포트가 해당 프로젝트에 속하는지 확인
            port = await self.uow.port.get_by_id_for_project(
                project_id=project_id,
                port_id=request.port_id,
            )
            if port is None:
                raise PortNotFound()

            # DNS에 포트 바인딩
            dns = await self.uow.dns.bind_port(dns_id, project_id, request.port_id)
            await self.project_resource_client.mapping_dns_and_port()
            return dns
