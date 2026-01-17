from fastapi import Depends

from src.app.dns.models import DNS
from src.app.dns.schemas import DNSPortBinding
from src.app.dns.exceptions import DNSNotFound
from src.app.project.exceptions import ProjectNotFound
from src.app.port.exceptions import PortNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class BindPortToDNSUseCase(BaseUseCase):
    """DNS에 공개 포트를 바인딩하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        dns_id: str,
        request: DNSPortBinding,
        user_id: str,
    ) -> DNS:
        # 프로젝트 확인
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

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
        dns.bind_port(request.port_id)
        return dns
