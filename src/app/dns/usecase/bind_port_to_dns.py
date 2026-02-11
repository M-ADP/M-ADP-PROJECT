from src.app.dns.model import DNS
from src.app.dns.schemas import DNSPortBinding
from src.app.dns.exceptions import DNSNotFound
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManageDNS
from src.app.port.exceptions import PortNotFound
from src.core.usecase import BaseUseCase


class BindPortToDNSUseCase(BaseUseCase):
    """DNS에 공개 포트를 바인딩하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        dns_id: str,
        request: DNSPortBinding,
        user_id: str,
    ) -> DNS:
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
